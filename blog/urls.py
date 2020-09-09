from django.conf.urls import url
from blog import views

urlpatterns = [
    url(r'up_down/$',views.up_down),
    url(r'(\w+)/article/(\d+)/$',views.article_detail), #文章详情 article_detail(request,xiaohei,1)
    url(r'(\w+)/$',views.home),#home(request,username)

]
