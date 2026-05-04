from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Resume
from .services import ResumeParserService
from .forms import ResumeEditForm
import os


@login_required
@require_http_methods(["GET", "POST"])
def upload_resume(request):
    """上传简历"""
    if request.method == 'POST' and request.FILES.get('resume_file'):
        file = request.FILES['resume_file']

        print(f"\n[上传] 接收到文件: {file.name}, 大小: {file.size} bytes")

        # 检查文件类型
        if not (file.name.endswith('.pdf') or file.name.endswith('.docx') or file.name.endswith('.doc')):
            print(f"[上传] 文件类型错误: {file.name}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': '仅支持PDF和Word格式'}, status=400)
            messages.error(request, '仅支持PDF和Word格式')
            return redirect('upload_resume')

        # 创建简历记录
        resume = Resume.objects.create(
            user=request.user,
            file=file,
            file_name=file.name,
            status='pending'
        )
        print(f"[上传] 简历记录已创建, ID={resume.id}")

        # 解析简历
        try:
            file_path = resume.file.path
            print(f"\n{'=' * 60}")
            print(f"[简历上传] 用户={request.user.username}, 文件={file.name}")
            print(f"{'=' * 60}")

            # 步骤1：提取文本
            print(f"[步骤1/4] 正在提取文本...")
            text = ResumeParserService.extract_text(file_path)
            if not text:
                print(f"[错误] 无法提取文件内容")
                resume.status = 'failed'
                resume.save()
                messages.error(request, '无法提取文件内容，请确保文件格式正确')
                return redirect('resume_list')

            print(f"[步骤1/4] ✓ 文本提取成功，长度={len(text)}字符")
            resume.raw_text = text
            resume.save()

            # 步骤2：AI解析
            print(f"[步骤2/4] 正在调用AI解析...")
            parsed_data = ResumeParserService.parse_with_ai(text)
            if not parsed_data:
                print(f"[错误] AI解析失败")
                resume.status = 'failed'
                resume.save()
                messages.warning(request, 'AI解析失败，请检查文件内容或稍后重试')
                return redirect('resume_list')

            print(f"[步骤2/4] ✓ AI解析成功")
            resume.parsed_data = parsed_data
            resume.name = parsed_data.get('name', '')
            resume.gender = parsed_data.get('gender', '')
            resume.age = parsed_data.get('age')
            resume.phone = parsed_data.get('phone', '')
            resume.email = parsed_data.get('email', '')
            resume.education = parsed_data.get('education', '')
            resume.school = parsed_data.get('school', '')
            resume.major = parsed_data.get('major', '')
            resume.work_years = parsed_data.get('work_years')
            resume.status = 'parsed'

            # 步骤3：计算简历评分
            print(f"[步骤3/4] 正在计算简历评分...")
            score, score_details = ResumeParserService.calculate_resume_score(text, parsed_data)
            resume.score = score
            resume.score_details = score_details
            resume.save()
            print(f"[步骤3/4] ✓ 评分完成，总分={score}分")

            # 步骤4：自动匹配岗位（仅求职者）
            # 临时禁用自动匹配，加快上传速度
            match_count = 0
            print(f"[步骤4/4] 跳过自动岗位匹配（可在简历列表手动匹配）")
            messages.success(request, f'简历解析成功！当前评分：{score}分。可在"智能匹配岗位"页面手动匹配。')

            # 自动匹配
            # if request.user.user_type == 'jobseeker':
            #     print(f"[步骤4/4] 正在匹配岗位...")
            #     from apps.jobs.services import JobMatchService
            #     match_results = JobMatchService.match_jobs_for_resume(resume)
            #     match_count = len(match_results)
            #     print(f"[步骤4/4] ✓ 匹配完成，找到{match_count}个岗位")
            #     messages.success(request, f'简历解析成功！当前评分：{score}分，已为您匹配 {match_count} 个合适的岗位')
            # else:
            #     messages.success(request, f'简历解析成功！当前评分：{score}分')

            print(f"{'=' * 60}")
            print(f"[简历上传] ✅ 全部完成！")
            print(f"{'=' * 60}\n")

            # 如果是Ajax请求，返回JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'resume_id': resume.id,
                    'score': score,
                    'match_count': match_count,
                    'message': f'简历解析成功！评分：{score}分'
                })

        except Exception as e:
            print(f"[错误] 解析异常: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            resume.status = 'failed'
            resume.save()

            # 如果是Ajax请求，返回JSON错误
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': f'解析出错：{str(e)}'
                }, status=500)

            messages.error(request, f'解析出错：{str(e)}')

        return redirect('resume_list')

    return render(request, 'resumes/upload.html')


@login_required
def resume_list(request):
    """简历列表"""
    if request.user.user_type == 'jobseeker':
        resumes = Resume.objects.filter(user=request.user).order_by('-created_at')
    else:
        # HR可以看到所有简历（用于匹配）
        resumes = Resume.objects.filter(status='parsed').order_by('-created_at')

    return render(request, 'resumes/list.html', {'resumes': resumes})


@login_required
def resume_detail(request, resume_id):
    """简历详情"""
    resume = get_object_or_404(Resume, id=resume_id)

    # 权限检查
    if request.user.user_type == 'jobseeker' and resume.user != request.user:
        messages.error(request, '无权查看')
        return redirect('resume_list')

    return render(request, 'resumes/detail.html', {'resume': resume})


@login_required
@require_http_methods(["POST"])
def delete_resume(request, resume_id):
    """删除简历"""
    resume = get_object_or_404(Resume, id=resume_id)

    # 权限检查
    if resume.user != request.user:
        messages.error(request, '无权删除该简历')
        return redirect('resume_list')

    try:
        # 删除文件
        if resume.file:
            if os.path.exists(resume.file.path):
                os.remove(resume.file.path)

        # 删除记录
        resume.delete()
        messages.success(request, '简历已删除')
    except Exception as e:
        messages.error(request, f'删除失败：{str(e)}')

    return redirect('resume_list')


@login_required
@require_http_methods(["GET", "POST"])
def edit_resume(request, resume_id):
    """编辑简历"""
    resume = get_object_or_404(Resume, id=resume_id)

    # 权限检查
    if resume.user != request.user:
        messages.error(request, '无权编辑该简历')
        return redirect('resume_list')

    if request.method == 'POST':
        form = ResumeEditForm(request.POST, instance=resume)
        if form.is_valid():
            updated_resume = form.save(commit=False)

            # 更新parsed_data中的信息
            if updated_resume.parsed_data:
                updated_resume.parsed_data['name'] = updated_resume.name
                updated_resume.parsed_data['gender'] = updated_resume.gender
                updated_resume.parsed_data['age'] = updated_resume.age
                updated_resume.parsed_data['phone'] = updated_resume.phone
                updated_resume.parsed_data['email'] = updated_resume.email
                updated_resume.parsed_data['education'] = updated_resume.education
                updated_resume.parsed_data['school'] = updated_resume.school
                updated_resume.parsed_data['major'] = updated_resume.major
                updated_resume.parsed_data['work_years'] = updated_resume.work_years

            # 重新计算评分
            if updated_resume.raw_text and updated_resume.parsed_data:
                score, score_details = ResumeParserService.calculate_resume_score(
                    updated_resume.raw_text,
                    updated_resume.parsed_data
                )
                updated_resume.score = score
                updated_resume.score_details = score_details

            updated_resume.save()
            messages.success(request, '简历更新成功！')
            return redirect('resume_detail', resume_id=resume.id)
    else:
        form = ResumeEditForm(instance=resume)

    return render(request, 'resumes/edit.html', {'form': form, 'resume': resume})


@login_required
@require_http_methods(["POST"])
def optimize_resume(request, resume_id):
    """优化简历"""
    resume = get_object_or_404(Resume, id=resume_id)

    # 权限检查
    if resume.user != request.user:
        return JsonResponse({'error': '无权操作'}, status=403)

    if not resume.raw_text:
        return JsonResponse({'error': '简历未解析'}, status=400)

    # 生成优化建议
    suggestions = ResumeParserService.optimize_resume(resume.raw_text)
    resume.optimization_suggestions = suggestions
    resume.save()

    return JsonResponse({'suggestions': suggestions})


@login_required
@require_http_methods(["POST"])
def generate_optimized_resume(request, resume_id):
    """生成优化后的简历"""
    original_resume = get_object_or_404(Resume, id=resume_id)

    # 权限检查
    if original_resume.user != request.user:
        return JsonResponse({'success': False, 'error': '无权操作'}, status=403)

    # 检查是否有优化建议
    if not original_resume.optimization_suggestions:
        return JsonResponse({'success': False, 'error': '请先生成优化建议'}, status=400)

    if not original_resume.raw_text:
        return JsonResponse({'success': False, 'error': '原始简历内容为空'}, status=400)

    try:
        # 生成优化后的简历内容
        optimized_content = ResumeParserService.generate_optimized_resume_content(
            original_resume.raw_text,
            original_resume.optimization_suggestions,
            original_resume.parsed_data
        )

        if not optimized_content:
            return JsonResponse({'success': False, 'error': 'AI生成失败，请稍后重试'}, status=500)

        # 创建新的简历记录
        new_resume = Resume.objects.create(
            user=request.user,
            file_name=f"{original_resume.file_name.rsplit('.', 1)[0]}_优化版.txt",
            raw_text=optimized_content,
            status='pending'
        )

        # 解析优化后的简历
        parsed_data = ResumeParserService.parse_with_ai(optimized_content)
        if parsed_data:
            new_resume.parsed_data = parsed_data
            new_resume.name = parsed_data.get('name', original_resume.name)
            new_resume.gender = parsed_data.get('gender', original_resume.gender)
            new_resume.age = parsed_data.get('age', original_resume.age)
            new_resume.phone = parsed_data.get('phone', original_resume.phone)
            new_resume.email = parsed_data.get('email', original_resume.email)
            new_resume.education = parsed_data.get('education', original_resume.education)
            new_resume.school = parsed_data.get('school', original_resume.school)
            new_resume.major = parsed_data.get('major', original_resume.major)
            new_resume.work_years = parsed_data.get('work_years', original_resume.work_years)
            new_resume.status = 'parsed'

            # 计算优化后的评分
            score, score_details = ResumeParserService.calculate_resume_score(optimized_content, parsed_data)
            new_resume.score = score
            new_resume.score_details = score_details
        else:
            # 如果解析失败，使用原简历的基本信息
            new_resume.name = original_resume.name
            new_resume.gender = original_resume.gender
            new_resume.age = original_resume.age
            new_resume.phone = original_resume.phone
            new_resume.email = original_resume.email
            new_resume.education = original_resume.education
            new_resume.school = original_resume.school
            new_resume.major = original_resume.major
            new_resume.work_years = original_resume.work_years
            new_resume.parsed_data = original_resume.parsed_data
            new_resume.status = 'parsed'

            # 使用原评分或重新计算
            if optimized_content:
                score, score_details = ResumeParserService.calculate_resume_score(optimized_content,
                                                                                  original_resume.parsed_data)
                new_resume.score = score
                new_resume.score_details = score_details

        new_resume.save()

        return JsonResponse({
            'success': True,
            'new_resume_id': new_resume.id,
            'message': '优化简历生成成功'
        })

    except Exception as e:
        print(f"生成优化简历错误: {e}")
        return JsonResponse({'success': False, 'error': f'生成失败: {str(e)}'}, status=500)

