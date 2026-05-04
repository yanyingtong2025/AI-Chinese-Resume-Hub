from django.db import models
from apps.users.models import User
from apps.resumes.models import Resume


class Job(models.Model):
    """岗位模型"""
    hr_user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='发布HR', related_name='jobs')
    title = models.CharField('岗位名称', max_length=200)
    company = models.CharField('公司名称', max_length=200, default='', blank=True)
    department = models.CharField('部门', max_length=100, blank=True)
    location = models.CharField('工作地点', max_length=200)
    salary_min = models.IntegerField('最低薪资(k)', null=True, blank=True)
    salary_max = models.IntegerField('最高薪资(k)', null=True, blank=True)

    # 岗位要求
    education_required = models.CharField('学历要求', max_length=50)
    work_years_required = models.IntegerField('工作年限要求')
    skills_required = models.TextField('技能要求', help_text='用逗号分隔')
    job_description = models.TextField('岗位描述')
    job_requirements = models.TextField('任职要求')

    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'jobs'
        verbose_name = '岗位'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Application(models.Model):
    """投递记录模型"""
    job = models.ForeignKey(Job, on_delete=models.CASCADE, verbose_name='岗位', related_name='applications')
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, verbose_name='简历', related_name='applications')
    jobseeker = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='求职者', related_name='applications')

    # 投递状态
    STATUS_CHOICES = (
        ('pending', '待查看'),
        ('viewed', '已查看'),
        ('interested', '感兴趣'),
        ('interview', '邀请面试'),
        ('rejected', '不合适'),
    )
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')

    # HR备注
    hr_notes = models.TextField('HR备注', blank=True)

    # 时间记录
    created_at = models.DateTimeField('投递时间', auto_now_add=True)
    viewed_at = models.DateTimeField('查看时间', null=True, blank=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'applications'
        verbose_name = '投递记录'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        unique_together = ['job', 'resume']

    def __str__(self):
        return f"{self.jobseeker.username} 投递 {self.job.title}"


class MatchResult(models.Model):
    """匹配结果模型"""
    job = models.ForeignKey(Job, on_delete=models.CASCADE, verbose_name='岗位', related_name='match_results')
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, verbose_name='简历', related_name='match_results')

    # 匹配结果
    match_score = models.FloatField('匹配分数', help_text='0-100分')
    match_analysis = models.TextField('匹配分析', blank=True)

    # 各维度评分
    education_score = models.FloatField('学历匹配度', default=0)
    experience_score = models.FloatField('经验匹配度', default=0)
    skills_score = models.FloatField('技能匹配度', default=0)

    # 面试建议
    interview_suggestions = models.TextField('面试建议', blank=True)

    # HR操作
    STATUS_CHOICES = (
        ('pending', '待处理'),
        ('interested', '感兴趣'),
        ('interview', '邀请面试'),
        ('rejected', '不合适'),
    )
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    hr_notes = models.TextField('HR备注', blank=True)

    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'match_results'
        verbose_name = '匹配结果'
        verbose_name_plural = verbose_name
        ordering = ['-match_score', '-created_at']
        unique_together = ['job', 'resume']

    def __str__(self):
        return f"{self.job.title} - {self.resume.name} ({self.match_score}分)"


class MatchWeightConfig(models.Model):
    """匹配权重配置"""
    job = models.OneToOneField('Job', on_delete=models.CASCADE, verbose_name='岗位', related_name='weight_config')

    education_weight = models.FloatField('学历权重', default=0.3, help_text='0-1之间')
    experience_weight = models.FloatField('经验权重', default=0.4, help_text='0-1之间')
    skills_weight = models.FloatField('技能权重', default=0.3, help_text='0-1之间')

    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'match_weight_configs'
        verbose_name = '匹配权重配置'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.job.title}的权重配置"

    def clean(self):
        """验证权重总和为1"""
        from django.core.exceptions import ValidationError
        total = self.education_weight + self.experience_weight + self.skills_weight
        if abs(total - 1.0) > 0.01:
            raise ValidationError('权重总和必须为1.0')


class MatchingSession(models.Model):
    """匹配会话历史记录"""
    job = models.ForeignKey(Job, on_delete=models.CASCADE, verbose_name='岗位', related_name='matching_sessions')
    hr_user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='HR用户')

    total_resumes = models.IntegerField('简历总数', default=0)
    matched_count = models.IntegerField('匹配数量', default=0)
    avg_score = models.FloatField('平均分数', default=0)

    # 分段统计
    excellent_count = models.IntegerField('优秀(80+)', default=0)
    good_count = models.IntegerField('良好(60-80)', default=0)
    fair_count = models.IntegerField('一般(40-60)', default=0)
    poor_count = models.IntegerField('较差(<40)', default=0)

    created_at = models.DateTimeField('匹配时间', auto_now_add=True)

    class Meta:
        db_table = 'matching_sessions'
        verbose_name = '匹配会话记录'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.job.title} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

