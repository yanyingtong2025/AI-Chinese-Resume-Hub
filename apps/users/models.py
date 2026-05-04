from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """用户模型"""
    USER_TYPE_CHOICES = (
        ('jobseeker', '求职者'),
        ('hr', 'HR'),
    )

    user_type = models.CharField('用户类型', max_length=20, choices=USER_TYPE_CHOICES)
    phone = models.CharField('手机号', max_length=20, blank=True)
    company = models.CharField('公司名称', max_length=200, blank=True, help_text='仅HR需要填写')
    avatar = models.ImageField('头像', upload_to='avatars/', blank=True, null=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"

