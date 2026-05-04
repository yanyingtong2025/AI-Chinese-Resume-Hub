from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from .models import Job, Application, MatchResult
from apps.resumes.models import Resume
from .services import JobMatchService


@login_required
@require_http_methods(["GET", "POST"])
def create_job(request):
    """创建岗位"""
    if request.user.user_type != 'hr':
        messages.error(request, '仅HR可创建岗位')
        return redirect('hr_dashboard')

    if request.method == 'POST':
        job = Job.objects.create(
            hr_user=request.user,
            title=request.POST.get('title'),
            company=request.POST.get('company', ''),
            department=request.POST.get('department', ''),
            location=request.POST.get('location'),
            salary_min=request.POST.get('salary_min') or None,
            salary_max=request.POST.get('salary_max') or None,
            education_required=request.POST.get('education_required'),
            work_years_required=request.POST.get('work_years_required'),
            skills_required=request.POST.get('skills_required'),
            job_description=request.POST.get('job_description'),
            job_requirements=request.POST.get('job_requirements'),
        )

        messages.success(request, '岗位创建成功')
        return redirect('job_detail', job_id=job.id)

    return render(request, 'jobs/create.html')


@login_required
def job_detail(request, job_id):
    """岗位详情"""
    job = get_object_or_404(Job, id=job_id)

    # HR才能看到匹配结果
    if request.user.user_type == 'hr' and job.hr_user == request.user:
        match_results = MatchResult.objects.filter(job=job).order_by('-match_score')[:20]
        statistics = JobMatchService.get_match_statistics(job)
    else:
        match_results = []
        statistics = None

    context = {
        'job': job,
        'match_results': match_results,
        'statistics': statistics,
    }

    return render(request, 'jobs/detail.html', context)


@login_required
def job_list(request):
    """岗位列表"""
    if request.user.user_type == 'hr':
        jobs = Job.objects.filter(hr_user=request.user).order_by('-created_at')
    else:
        jobs = Job.objects.filter(is_active=True).order_by('-created_at')

    return render(request, 'jobs/list.html', {'jobs': jobs})


@login_required
def edit_job(request, job_id):
    """编辑岗位"""
    job = get_object_or_404(Job, id=job_id)

    # 权限检查
    if request.user.user_type != 'hr' or job.hr_user != request.user:
        messages.error(request, '无权操作')
        return redirect('job_list')

    if request.method == 'POST':
        job.title = request.POST.get('title')
        job.company = request.POST.get('company', '')
        job.department = request.POST.get('department', '')
        job.location = request.POST.get('location')
        job.salary_min = request.POST.get('salary_min') or None
        job.salary_max = request.POST.get('salary_max') or None
        job.education_required = request.POST.get('education_required')
        job.work_years_required = request.POST.get('work_years_required')
        job.skills_required = request.POST.get('skills_required')
        job.job_description = request.POST.get('job_description')
        job.job_requirements = request.POST.get('job_requirements')
        job.is_active = request.POST.get('is_active') == 'on'
        job.save()

        messages.success(request, '岗位更新成功')
        return redirect('job_detail', job_id=job.id)

    return render(request, 'jobs/edit.html', {'job': job})


@login_required
@require_http_methods(["POST"])
def apply_job(request, job_id):
    """投递简历到岗位"""
    job = get_object_or_404(Job, id=job_id)

    # 权限检查
    if request.user.user_type != 'jobseeker':
        return JsonResponse({'success': False, 'error': '仅求职者可投递简历'}, status=403)

    resume_id = request.POST.get('resume_id')
    if not resume_id:
        return JsonResponse({'success': False, 'error': '请选择简历'}, status=400)

    resume = get_object_or_404(Resume, id=resume_id, user=request.user)

    # 检查是否已投递
    existing = Application.objects.filter(job=job, resume=resume).first()
    if existing:
        return JsonResponse({'success': False, 'error': '您已经投递过该岗位'}, status=400)

    # 创建投递记录
    application = Application.objects.create(
        job=job,
        resume=resume,
        jobseeker=request.user,
        status='pending'
    )

    return JsonResponse({
        'success': True,
        'message': '投递成功！HR将尽快查看您的简历'
    })


@login_required
def my_applications(request):
    """我的投递记录（求职者）"""
    if request.user.user_type != 'jobseeker':
        messages.error(request, '仅求职者可查看投递记录')
        return redirect('/')

    applications = Application.objects.filter(jobseeker=request.user).select_related('job', 'resume')

    return render(request, 'jobs/my_applications.html', {'applications': applications})


@login_required
def job_applications(request, job_id):
    """查看岗位的投递记录（HR）"""
    job = get_object_or_404(Job, id=job_id)

    # 权限检查
    if request.user.user_type != 'hr' or job.hr_user != request.user:
        messages.error(request, '无权查看')
        return redirect('job_list')

    applications = Application.objects.filter(job=job).select_related('resume', 'jobseeker').order_by('-created_at')

    # 统计
    stats = {
        'total': applications.count(),
        'pending': applications.filter(status='pending').count(),
        'interested': applications.filter(status='interested').count(),
        'interview': applications.filter(status='interview').count(),
    }

    return render(request, 'jobs/applications.html', {
        'job': job,
        'applications': applications,
        'stats': stats,
    })


@login_required
@require_http_methods(["POST"])
def update_application_status(request, application_id):
    """更新投递状态（HR）"""
    application = get_object_or_404(Application, id=application_id)

    # 权限检查
    if request.user.user_type != 'hr' or application.job.hr_user != request.user:
        return JsonResponse({'success': False, 'error': '无权操作'}, status=403)

    # 获取参数，如果没有提供则保持原值
    status = request.POST.get('status')
    hr_notes = request.POST.get('hr_notes')

    # 只更新提供的字段
    if status is not None:
        application.status = status
        if status == 'viewed' and not application.viewed_at:
            application.viewed_at = timezone.now()

    if hr_notes is not None:
        application.hr_notes = hr_notes

    application.save()

    return JsonResponse({'success': True, 'message': '状态更新成功'})


@login_required
@require_http_methods(["POST"])
def start_matching(request, job_id):
    """开始匹配简历"""
    job = get_object_or_404(Job, id=job_id)

    # 权限检查
    if request.user.user_type != 'hr' or job.hr_user != request.user:
        return JsonResponse({'error': '无权操作'}, status=403)

    # 批量匹配
    match_results = JobMatchService.batch_match(job)

    return JsonResponse({
        'success': True,
        'count': len(match_results),
        'message': f'成功匹配 {len(match_results)} 份简历'
    })


@login_required
def match_detail(request, match_id):
    """匹配详情"""
    match = get_object_or_404(MatchResult, id=match_id)

    # 权限检查
    if request.user.user_type != 'hr' or match.job.hr_user != request.user:
        messages.error(request, '无权查看')
        return redirect('job_list')

    return render(request, 'jobs/match_detail.html', {'match': match})


@login_required
def match_results(request, job_id):
    """匹配结果页面"""
    job = get_object_or_404(Job, id=job_id)

    # 权限检查
    if request.user.user_type != 'hr' or job.hr_user != request.user:
        messages.error(request, '无权查看')
        return redirect('job_list')

    # 筛选参数
    min_score = request.GET.get('min_score', 60)
    education = request.GET.get('education', '')
    min_work_years = request.GET.get('min_work_years', '')

    # 获取匹配结果
    results = MatchResult.objects.filter(job=job, match_score__gte=min_score)

    if education:
        results = results.filter(resume__education=education)

    if min_work_years:
        results = results.filter(resume__work_years__gte=int(min_work_years))

    results = results.order_by('-match_score')

    # 统计数据
    statistics = JobMatchService.get_match_statistics(job)

    context = {
        'job': job,
        'results': results,
        'statistics': statistics,
        'min_score': min_score,
    }

    return render(request, 'jobs/match_results.html', context)


@login_required
@require_http_methods(["POST"])
def update_match_status(request, match_id):
    """更新匹配状态"""
    match = get_object_or_404(MatchResult, id=match_id)

    # 权限检查
    if request.user.user_type != 'hr' or match.job.hr_user != request.user:
        return JsonResponse({'error': '无权操作'}, status=403)

    status = request.POST.get('status')
    hr_notes = request.POST.get('hr_notes', '')

    match.status = status
    match.hr_notes = hr_notes
    match.save()

    return JsonResponse({'success': True})


@login_required
def matched_jobs(request):
    """求职者查看匹配的岗位"""
    if request.user.user_type != 'jobseeker':
        messages.error(request, '仅求职者可查看匹配岗位')
        return redirect('job_list')

    # 获取筛选参数
    min_score = int(request.GET.get('min_score', 0))
    resume_id = request.GET.get('resume_id', '')

    # 构建查询
    all_matches = MatchResult.objects.filter(
        resume__user=request.user,
        job__is_active=True,
        match_score__gte=min_score
    ).select_related('job', 'job__hr_user', 'resume')

    if resume_id:
        # 如果指定了简历，按匹配度排序（不去重，显示所有匹配）
        matches = list(all_matches.filter(resume_id=resume_id).order_by('-match_score'))
        print(f"[匹配岗位] 简历ID={resume_id}, 匹配数量={len(matches)}")
        for match in matches:
            print(f"  - 岗位: {match.job.title} (ID={match.job_id}), 分数={match.match_score}")
    else:
        # 如果是查看全部简历，需要去重：每个岗位只显示匹配度最高的记录
        all_matches_list = list(all_matches.order_by('job_id', '-match_score'))
        seen_jobs = set()
        matches = []
        for match in all_matches_list:
            if match.job_id not in seen_jobs:
                seen_jobs.add(match.job_id)
                matches.append(match)
        # 按匹配度重新排序
        matches = sorted(matches, key=lambda x: x.match_score, reverse=True)
        print(f"[匹配岗位] 查看全部，原始={len(all_matches_list)}, 去重后={len(matches)}")

    # 获取用户的简历列表用于筛选
    user_resumes = Resume.objects.filter(user=request.user, status='parsed')

    # 统计数据（基于实际显示的matches）
    stats = {
        'total': len(matches),
        'excellent': sum(1 for m in matches if m.match_score >= 80),
        'good': sum(1 for m in matches if 60 <= m.match_score < 80),
        'fair': sum(1 for m in matches if m.match_score < 60),
    }

    context = {
        'matches': matches,
        'stats': stats,
        'min_score': min_score,
        'selected_resume_id': resume_id,
        'user_resumes': user_resumes,
    }

    return render(request, 'jobs/matched_jobs.html', context)
