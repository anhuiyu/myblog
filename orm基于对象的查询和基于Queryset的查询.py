import os
if __name__=='__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bbs.settings")
    import django
    django.setup()
    from blog import models
    #基于对象的查询SQL：子查询
    # a1=models.Article.objects.first()
    # print(a1.user.avatar,type(a1.user),a1.desc)

    #基于QuerySet查询，SQL:join连表查询
    # a2=models.Article.objects.filter(pk=1)
    # print(a2.values("user__avatar"))

    #查询a1对应的评论数
    # ret=models.Article.objects.first().comment_set.all()
    # print(ret)

    #查询某个分类对应的文章
    from django.db.models import Count
    user=models.UserInfo.objects.filter(username="yubatian").first()#H获得yubatian用户
    # ret=models.Article.objects.filter(user=user).extra(
    #     select={"archive_ym":"date_format(create_time,'%%Y-%%m')"}
    # ).values("archive_ym").annotate(c=Count("nid")).values("archive_ym","c")
    # print(ret)

    blog=user.blog#根据用户取得站点
    # ret=models.Category.objects.filter(blog=blog)#求yubatian站点下面所有的文章分类
    # ret=ret[0].article_set.all()#python分类下所有的文章
    # for i in ret:
    #     print(i.title,i.article_set.all().count())
    #上面4行语句可以用一行语句代替
    # ret=models.Category.objects.filter(blog=blog).annotate(c=Count("article")).values("title","c")
    # print(ret)
    
    #由文章表查询tag表
    ret=models.Article.objects.filter(user=user).filter(tag__title="python")
    print(ret)


