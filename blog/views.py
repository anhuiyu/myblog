from django.shortcuts import render,HttpResponse,redirect
from django.contrib import  auth
from .forms import RegForm
from .models import UserInfo
from blog import models
from django.http import JsonResponse
from PIL import Image,ImageDraw,ImageFont
from io import BytesIO
from django.db.models import Count
import random
import json,os
from django.db.models import F
import logging
from bbs import settings
from bs4 import BeautifulSoup
from utils.mypage import Page
#生成一个logger实例，专门用来记录日志
logger=logging.getLogger(__name__)

# Create your views here.
#注册的视图函数
def register(request):
    if request.method=="POST":
        ret={"status":0,"msg":""}
        form_obj=RegForm(request.POST)
        #做校验
        if form_obj.is_valid():
            #校验通过，去数据库创建一个新的用户
            form_obj.cleaned_data.pop("re_password")
            avatar_img=request.FILES.get("avatar")
            UserInfo.objects.create_user(**form_obj.cleaned_data,avatar=avatar_img)
            ret["msg"]="/index/"
            return JsonResponse(ret)
        else:
            ret["status"]=1
            ret["msg"]=form_obj.errors
            return JsonResponse(ret)
    #生成一个form对象，返回给前台页面
    form_obj=RegForm()
    return render(request,"register.html",{"form_obj":form_obj})

#带验证码的登录
def login(request):
    if request.method=="POST":
        #初始化一个给AJAX返回的数据
        ret={"status":0,"msg":""}
        #从提交古来的数据中取到用户名和密码
        username=request.POST.get("username")
        pwd=request.POST.get("password")
        valid_code=request.POST.get("valid_code")
        if valid_code and valid_code.upper()==request.session.get("valid_code").upper():
            #验证码正确，利用auth模块做用户名和密码的校验
            user=auth.authenticate(username=username,password=pwd)
            if user:
                #用户名密码正确，给用户做登录
                auth.login(request,user)
                ret["msg"]="/blog/"+username
            else:
                #用户名密码错误
                ret["status"]=1
                ret["msg"]="用户名或密码错误！"
        else:
            ret["status"]=1
            ret["msg"]="验证码错误"
        return JsonResponse(ret)
    return render(request,"login.html")

def get_valid_img(request):
    #获取随机颜色的函数
    def get_random_color():
        return random.randint(0,255),random.randint(0,255),random.randint(0,255)

    #生成一个图片对象
    img_obj=Image.new(
        'RGB',
        (220,35),
        get_random_color()
    )
    # 在生成的图片上写字符
    # 生成一个图片画笔对象
    draw_obj = ImageDraw.Draw(img_obj)
    # 加载字体文件， 得到一个字体对象
    font_obj = ImageFont.truetype("static/font/kumo.ttf", 28)
    # 开始生成随机字符串并且写到图片上
    tmp_list = []
    for i in range(5):
        u = chr(random.randint(65, 90))  # 生成大写字母
        l = chr(random.randint(97, 122))  # 生成小写字母
        n = str(random.randint(0, 9))  # 生成数字，注意要转换成字符串类型

        tmp = random.choice([u, l, n])
        tmp_list.append(tmp)
        draw_obj.text((20+40*i, 0), tmp, fill=get_random_color(), font=font_obj)
    # 保存到session
    request.session["valid_code"] = "".join(tmp_list)
    io_obj=BytesIO()
    #将生成的图片数据保存在io对象中，直接在内存中加载即可
    img_obj.save(io_obj,"png")
    #从io对象里取上一步保存的数据
    data=io_obj.getvalue()
    return HttpResponse(data)

def index(request):
    page_num = request.GET.get("page")
    article_count = models.Article.objects.all().count()
    page_obj=Page(page_num, article_count, per_page=10, url_prefix="/index/", max_page=11,)
    article_list=models.Article.objects.all().order_by("nid").reverse()[page_obj.start:page_obj.end]
    page_html=page_obj.page_html()
    return render(request,"index.html",{"article_list":article_list,"page_html":page_html})

def logout(request):
    auth.logout(request)
    return redirect("/index/")

def check_username_exist(request):
    ret = {"status": 0, "msg": ""}
    username=request.GET.get("username")
    user_obj=models.UserInfo.objects.filter(username=username)
    if user_obj:
        ret["status"]=1
        ret["msg"]="用户名已注册"
    return JsonResponse(ret)

#个人博客主页
def home(request,username,*args):
    logger.debug("home视图获取到用户名:{}".format(username))
    user=models.UserInfo.objects.filter(username=username).first()
    if not  user:
        logger.warning("又有人访问不存在页面了")
        return HttpResponse("404")

    page_num = request.GET.get("page")

    #如果用户存则需要将TA写的所有文章找出来
    blog=user.blog
    #我的文章列表
    if not args:
        logger.debug("args没有接收到参数，默认走的是用户的个人博客页面")
        article_count = models.Article.objects.filter(user=user).count()
        article_list=models.Article.objects.filter(user=user).order_by("nid").reverse()
    else:
        logger.debug(args)
        logger.debug("----------------")
        #表示按照文章的分类或tag或日期归档查询
        if args[0]=="category":
            article_count = models.Article.objects.filter(user=user).filter(category__title=args[1]).count()
            article_list=models.Article.objects.filter(user=user).filter(category__title=args[1]).order_by("nid").reverse()
        elif args[0]=="tag":
            article_count = models.Article.objects.filter(user=user).filter(tag__title=args[1]).count()
            article_list = models.Article.objects.filter(user=user).filter(tag__title=args[1]).order_by("nid").reverse()
        else:
            try:
                year,month=args[1].split("-")
                logger.debug("分割得到参数year:{},month:{}".format(year,month))
                logger.debug("*******")
                article_count = models.Article.objects.filter(user=user).filter(
                    create_time__year=year, create_time__month=month
                ).count()
                article_list=models.Article.objects.filter(user=user).filter(
                    create_time__year=year,create_time__month=month
                ).order_by("nid").reverse()

            except Exception as e:
                logger.warning("请求访问的日志归档柜式不正确!!!")
                logger.warning(str(e))
                return HttpResponse("404")
    page_obj = Page(page_num, article_count, per_page=10, url_prefix="/blog/"+request.user.username, max_page=11, )
    article_list = article_list[page_obj.start:page_obj.end]
    print(article_list)
    page_html=page_obj.page_html()
    return render(request,"home.html",{
        "username":username,
        "blog":blog,
        "article_list":article_list,
        "page_html":page_html,
    })

def article_detail(request,username,pk):
    user=models.UserInfo.objects.filter(username=username).first()
    if not user:
        return HttpResponse("404")
    blog=user.blog
    #找到当前的文章
    article_obj=models.Article.objects.filter(pk=pk).first()
    #所有评论列表
    comment_list=models.Comment.objects.filter(article_id=pk)
    return render(
        request,
        "article_detail.html",
        {
            "username":username,
            "article":article_obj,
            "blog":blog,
            "comment_list":comment_list,
        }
    )

def up_down(request):
    article_id=request.POST.get("article_id")
    is_up=json.loads(request.POST.get("is_up"))
    user=request.user
    response={"state":True}
    try:
        models.ArticleUpDown.objects.create(user=user,article_id=article_id,is_up=is_up)
        models.Article.objects.filter(pk=article_id).update(up_count=F("up_count")+1)
    except Exception as e:
        print("1")
        response["state"]=False
        response["first_action"]=models.ArticleUpDown.objects.filter(user=user,article_id=article_id).first().is_up
        print(response)
    return JsonResponse(response)

def comment(request):
    pid=request.POST.get("pid")
    article_id=request.POST.get("article_id")
    content=request.POST.get("content")
    user_pk=request.user.pk
    response={}
    if not pid: #根评论
        comment_obj=models.Comment.objects.create(article_id=article_id,content=content,user_id=user_pk)
    else:
        comment_obj=models.Comment.objects.create(article_id=article_id,content=content,user_id=user_pk,parent_comment_id=pid)
    response["create_time"]=comment_obj.create_time.strftime("%Y-%m-%d")
    response["content"]=comment_obj.content
    response["username"]=comment_obj.user.username
    return JsonResponse(response)

# def comment_tree(request,article_id):
#     ret=list(models.Comment.objects.filter(article_id=article_id).values("pk","content","parent_comment_id"))
#     return JsonResponse(ret,safe=False)

def add_article(request):
    if request.method=="POST":
        title=request.POST.get("title")
        category_title=request.POST.get("category")
        category_obj=models.Category.objects.filter(title=category_title).first()
        tag_title=request.POST.get("tag")
        tag_obj=models.Tag.objects.filter(title=tag_title).first()
        article_content=request.POST.get("article_content")
        user=request.user
        #截取前150个字符，这里会选取真实的内容，不选标签
        bs=BeautifulSoup(article_content,"html.parser")
        desc=bs.text[0:150]+"..."
        #过滤非法标签
        for tag in bs.find_all():
            if tag.name in ["script","link"]:
                tag.decompose()
        article_obj=models.Article.objects.create(user=user,title=title,desc=desc,category=category_obj)
        models.ArticleDetail.objects.create(content=str(bs),article=article_obj)
        models.Article2Tag.objects.create(article=article_obj,tag=tag_obj)
        return redirect("/blog/"+request.user.username)
    blog = request.user.blog
    category_list = models.Category.objects.filter(blog=blog)
    tag_list = models.Tag.objects.filter(blog=blog)
    return render(request,"add_article.html",{"category_list":category_list,"tag_list":tag_list})

def upload(request):
    obj=request.FILES.get("upload_img")
    path=os.path.join(settings.MEDIA_ROOT,"add_article_img",obj.name)
    with open(path,"wb") as f:
        for line in obj:
            f.write(line)
        res={
            "error":0,
            "url":"/media/add_article_img/"+obj.name
        }
    return HttpResponse(json.dumps(res))