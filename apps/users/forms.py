from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class UserRegisterForm(UserCreationForm):
    """用户注册表单"""
    email = forms.EmailField(required=True, label='邮箱')
    user_type = forms.ChoiceField(
        choices=User.USER_TYPE_CHOICES,
        required=True,
        label='用户类型'
    )
    phone = forms.CharField(required=False, max_length=20, label='手机号')
    company = forms.CharField(required=False, max_length=200, label='公司名称')

    class Meta:
        model = User
        fields = ['username', 'email', 'user_type', 'phone', 'company', 'password1', 'password2']

    def clean_company(self):
        """验证公司字段"""
        user_type = self.cleaned_data.get('user_type')
        company = self.cleaned_data.get('company')

        if user_type == 'hr' and not company:
            raise forms.ValidationError('HR用户必须填写公司名称')

        return company


class UserLoginForm(forms.Form):
    """用户登录表单"""
    username = forms.CharField(max_length=150, label='用户名')
    password = forms.CharField(widget=forms.PasswordInput, label='密码')

