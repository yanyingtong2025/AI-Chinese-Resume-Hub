from django.db import models
from apps.users.models import User


class Resume(models.Model):
    """简历模型"""
    STATUS_CHOICES = (
        ('pending', '待解析'),
        ('parsed', '已解析'),
        ('failed', '解析失败'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='所属用户', related_name='resumes')
    file = models.FileField('简历文件', upload_to='resumes/%Y/%m/')
    file_name = models.CharField('文件名', max_length=255)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')

    # 解析后的结构化信息
    name = models.CharField('姓名', max_length=100, blank=True)
    gender = models.CharField('性别', max_length=10, blank=True)
    age = models.IntegerField('年龄', null=True, blank=True)
    phone = models.CharField('电话', max_length=20, blank=True)
    email = models.EmailField('邮箱', blank=True)
    education = models.CharField('学历', max_length=50, blank=True)
    school = models.CharField('毕业院校', max_length=200, blank=True)
    major = models.CharField('专业', max_length=200, blank=True)
    work_years = models.IntegerField('工作年限', null=True, blank=True)

    # 原始文本和JSON数据
    raw_text = models.TextField('原始文本', blank=True)
    parsed_data = models.JSONField('解析数据', null=True, blank=True, help_text='包含工作经历、项目经验、技能等')

    # AI优化建议
    optimization_suggestions = models.TextField('优化建议', blank=True)

    # 简历评分（0-100分）
    score = models.FloatField('简历评分', default=0, help_text='AI评分，满分100')
    score_details = models.JSONField('评分详情', null=True, blank=True, help_text='各维度评分')

    created_at = models.DateTimeField('上传时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'resumes'
        verbose_name = '简历'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name or '未命名'} - {self.file_name}"


