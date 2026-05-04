from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .models import User


@require_http_methods(["GET", "POST"])
def register_view(request):
    """注册视图"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        email = request.POST.get('email')
        user_type = request.POST.get('user_type')
        phone = request.POST.get('phone', '')
        company = request.POST.get('company', '')

        # 验证
        if password != password2:
            messages.error(request, '两次密码不一致')
            return render(request, 'users/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, '用户名已存在')
            return render(request, 'users/register.html')

        # 创建用户
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            user_type=user_type,
            phone=phone,
            company=company if user_type == 'hr' else ''
        )

        messages.success(request, '注册成功，请登录')
        return redirect('login')

    return render(request, 'users/register.html')


@require_http_methods(["GET", "POST"])
def login_view(request):
    """登录视图"""
    if request.user.is_authenticated:
            # 已登录，根据用户类型重定向
        if request.user.user_type == 'hr':
            return redirect('hr_dashboard')
        else:
            return redirect('jobseeker_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # 根据用户类型重定向
            if user.user_type == 'hr':
                return redirect('hr_dashboard')
            else:
                return redirect('jobseeker_dashboard')
        else:
            messages.error(request, '用户名或密码错误')

    return render(request, 'users/login.html')


def logout_view(request):
    """登出视图"""
    logout(request)
    messages.success(request, '已成功退出登录')
    return redirect('login')


@login_required
def hr_dashboard(request):
    """HR控制台"""
    if request.user.user_type != 'hr':
        messages.error(request, '权限不足')
        return redirect('jobseeker_dashboard')

    from apps.jobs.models import Job, MatchResult, Application

    # 统计数据
    total_jobs = Job.objects.filter(hr_user=request.user).count()
    active_jobs = Job.objects.filter(hr_user=request.user, is_active=True).count()
    total_matches = MatchResult.objects.filter(job__hr_user=request.user).count()
    pending_matches = MatchResult.objects.filter(job__hr_user=request.user, status='pending').count()

    # 投递统计
    total_applications = Application.objects.filter(job__hr_user=request.user).count()
    pending_applications = Application.objects.filter(job__hr_user=request.user, status='pending').count()

    # 最新岗位
    recent_jobs = Job.objects.filter(hr_user=request.user).order_by('-created_at')[:5]

    # 最新投递
    recent_applications = Application.objects.filter(
        job__hr_user=request.user
    ).select_related('job', 'resume', 'jobseeker').order_by('-created_at')[:5]

    context = {
        'total_jobs': total_jobs,
        'active_jobs': active_jobs,
        'total_matches': total_matches,
        'pending_matches': pending_matches,
        'total_applications': total_applications,
        'pending_applications': pending_applications,
        'recent_jobs': recent_jobs,
        'recent_applications': recent_applications,
    }

    return render(request, 'users/hr_dashboard.html', context)


@login_required
def jobseeker_dashboard(request):
    """求职者控制台"""
    if request.user.user_type != 'jobseeker':
        messages.error(request, '权限不足')
        return redirect('hr_dashboard')

    from apps.resumes.models import Resume
    from apps.jobs.models import MatchResult, Application

    # 统计数据
    total_resumes = Resume.objects.filter(user=request.user).count()
    parsed_resumes = Resume.objects.filter(user=request.user, status='parsed').count()

    # 投递统计
    total_applications = Application.objects.filter(jobseeker=request.user).count()

    # 获取匹配的岗位数量
    matched_jobs_count = MatchResult.objects.filter(
        resume__user=request.user,
        job__is_active=True
    ).values('job').distinct().count()

    # 最新简历
    recent_resumes = Resume.objects.filter(user=request.user).order_by('-created_at')[:5]

    # 推荐岗位（每个岗位只显示匹配度最高的记录，去重）
    all_matches = MatchResult.objects.filter(
        resume__user=request.user,
        job__is_active=True
    ).select_related('job', 'job__hr_user', 'resume').order_by('-match_score', 'job_id')

    # 手动去重，每个岗位只保留最高匹配度的记录
    seen_jobs = set()
    recommended_jobs = []
    for match in all_matches:
        if match.job_id not in seen_jobs:
            seen_jobs.add(match.job_id)
            recommended_jobs.append(match)
            if len(recommended_jobs) >= 5:  # 只取前5个
                break

    context = {
        'total_resumes': total_resumes,
        'parsed_resumes': parsed_resumes,
        'total_applications': total_applications,
        'matched_jobs_count': matched_jobs_count,
        'recent_resumes': recent_resumes,
        'recommended_jobs': recommended_jobs,
    }

    return render(request, 'users/jobseeker_dashboard.html', context)



