from django.shortcuts import render,HttpResponse
from django.contrib import  auth
from .forms import RegForm
from .models import UserInfo
from django.http import JsonResponse
from PIL import Image,ImageDraw,ImageFont
from io import BytesIO
import random


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
                ret["msg"]="/index/"
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
    return render(request,"index.html")
