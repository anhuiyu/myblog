"""
bbs 用到的form类
"""

#定义一个注册用的form类
from django import forms
from django.forms import widgets
from django.core.exceptions import ValidationError
from blog import models

#定义一个注册的form类
class RegForm(forms.Form):
    username=forms.CharField(
        max_length=16,
        label="用户名",
        error_messages={
            "max_length":"用户名最长16位",
            "required":"用户名不能为空",
        },
        widget=widgets.TextInput(
            attrs={"class":"form-control"}
        )
    )
    password=forms.CharField(
        min_length=6,
        label="密码",
        error_messages={
            "min_length":"密码至少6位",
            "required":"密码不能为空",
        },
        widget=widgets.PasswordInput(
            attrs={"class":"form-control"}
        )
    )
    re_password=forms.CharField(
        min_length=6,
        label="确认密码",
        error_messages={
            "min_length":"确认密码至少6位",
            "required":"确认密码不能为空",
        },
        widget=widgets.PasswordInput(
            attrs={"class":"form-control"}
        )
    )
    email=forms.EmailField(
        label="邮箱",
        error_messages={
            "invalid":"邮箱格式不正确",
            "required":"邮箱不能为空",
        },
        widget=widgets.EmailInput(
            attrs={"class": "form-control"}
        )
    )
    #重写email字段的局部钩子
    def clean_email(self):
        email=self.cleaned_data.get("email")
        is_exist=models.UserInfo.objects.filter(email=email)
        if is_exist:
            self.add_error("username",ValidationError("邮箱已注册"))
        else:
            return email

    #重写全局的钩子函数，对确认密码做校验
    def clean(self):
        password=self.cleaned_data.get("password")
        re_password=self.cleaned_data.get("re_password")
        if re_password and re_password !=password:
            self.add_error("re_password",ValidationError("两次密码不一致"))
        else:
            return self.cleaned_data