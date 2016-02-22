# -*- coding:utf-8 -*-

from .models import MyUser,Book,Image
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

class addBookForm(forms.ModelForm):

    class Meta:
        model=Book
        fields=['name','pub_date','price','author','category']

class addImageForm(forms.ModelForm):

    class Meta:
        model=Image
        fields='__all__'

class loginForm(forms.Form):

    # 不太确定是否可以这样做，sigh
    class Meta:
        model=MyUser
        fields='__all__'

    def __init__(self,*args,**kwargs):
        super(loginForm,self).__init__(*args,**kwargs)
        self.helper=FormHelper()
        self.helper.form_method='post'
        self.helper.form_action='/homepage/'
        self.helper.add_input(Submit('submit','Submit'))

class registrationForm(forms.Form):
    # 进行注册的时候要用到
    # 这个主要就在于理顺逻辑关系
    pass

class setPasswordForm(forms.Form):
    # 进行重新设置密码
    password_old=forms.CharField(max_length=128)
    password_new=forms.CharField(max_length=128)
    password_repeat=forms.CharField(max_length=128)


