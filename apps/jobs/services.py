"""
岗位匹配服务
"""
from apps.resumes.services import DeepSeekClient
import json
import re
import requests
from .models import Job, MatchResult
from apps.resumes.models import Resume


class JobMatchService:
    """岗位匹配服务类"""

    @staticmethod
    def match_resume_to_job(resume, job):
        """
        匹配单个简历到岗位
        使用AI进行智能匹配分析，考虑学历、经验、技能等多维度
        """
        if resume.status != 'parsed' or not resume.parsed_data:
            return None

        # 获取权重配置（如果有的话）
        try:
            weight_config = job.weight_config
            education_weight = weight_config.education_weight
            experience_weight = weight_config.experience_weight
            skills_weight = weight_config.skills_weight
        except:
            # 默认权重
            education_weight = 0.25
            experience_weight = 0.40
            skills_weight = 0.35

        # 构建详细的简历信息
        resume_info = f"""
姓名：{resume.name}
学历：{resume.education}
毕业院校：{resume.school}
专业：{resume.major}
工作年限：{resume.work_years}年
技能清单：{', '.join(resume.parsed_data.get('skills', []))}

工作经历详情：
"""
        work_experience = resume.parsed_data.get('work_experience', [])
        if work_experience:
            for idx, exp in enumerate(work_experience, 1):
                resume_info += f"""
{idx}. {exp.get('company', '未知公司')} - {exp.get('position', '未知职位')}
   时间：{exp.get('duration', '未知')}
   工作内容：{exp.get('description', '无描述')}
"""
        else:
            resume_info += "暂无工作经历\n"

        # 项目经验
        projects = resume.parsed_data.get('projects', [])
        if projects:
            resume_info += "\n项目经验：\n"
            for idx, proj in enumerate(projects, 1):
                resume_info += f"{idx}. {proj.get('name', '未知项目')} - {proj.get('description', '')}\n"

        # 构建岗位要求信息
        job_info = f"""
岗位名称：{job.title}
公司名称：{job.company}
工作地点：{job.location}
学历要求：{job.education_required}
工作年限要求：{job.work_years_required}年以上
技能要求：{job.skills_required}

岗位描述：
{job.job_description}

任职要求：
{job.job_requirements}
"""

        # 优化后的AI匹配Prompt - 更精确的评分标准
        prompt = f"""你是一位资深的HR专家和人才评估顾问，拥有10年以上的招聘经验。请对以下候选人进行客观、细致的岗位匹配度分析。

【候选人简历】
{resume_info}

【目标岗位信息】
{job_info}

【评分权重说明】
- 学历匹配权重：{education_weight * 100:.0f}%
- 工作经验权重：{experience_weight * 100:.0f}%
- 技能匹配权重：{skills_weight * 100:.0f}%

【详细评分标准】

**1. 学历匹配度评分 (0-100分)**
评分规则：
- 完全符合要求：70-80分（不要轻易给90分以上）
- 超过要求（如要求本科给了硕士）：80-90分
- 略低于要求但可接受：50-70分
- 明显不符合要求：30-50分
- 完全不匹配：0-30分

考虑因素：
- 学历层次是否达标（专科/本科/硕士/博士）
- 毕业院校层次（985/211/普通本科/其他）
- 专业相关性（计算机、软件工程等技术专业相关度高）
- 如果简历学历为"本科"，岗位要求"本科"，应该给70-75分左右，不要给100分

**2. 工作经验匹配度评分 (0-100分)**
评分规则：
- 工作年限完全达标且经验高度相关：75-85分
- 工作年限达标但相关性一般：60-75分
- 工作年限略低但有相关经验：50-65分
- 工作年限明显不足：30-50分
- 几乎无相关经验：0-30分

考虑因素：
- 实际工作年限 vs 要求年限（例如：2年 vs 2年 = 达标）
- 工作经历的相关性（行业、岗位匹配度）
- 公司背景和平台（大厂、创业公司、传统企业）
- 项目经验的质量和深度
- 职位晋升轨迹
- **重要：如果候选人工作年限等于或超过要求，不应该给0分！**

**3. 技能匹配度评分 (0-100分)**
评分规则：
- 具备80%以上要求技能且有深度：80-90分
- 具备60-80%要求技能：65-80分
- 具备40-60%要求技能：50-65分
- 具备20-40%要求技能：30-50分
- 技能严重不足：0-30分

考虑因素：
- 核心技能覆盖率（仔细对比候选人技能和岗位要求）
- 技能的实际应用经验（项目中是否用过）
- 技术栈的深度和广度
- 学习能力和技术敏感度
- 额外加分技能

**4. 综合匹配度计算**
综合分数 = 学历分数 × {education_weight} + 经验分数 × {experience_weight} + 技能分数 × {skills_weight}

分数区间判断：
- 85-100分：非常匹配，强烈推荐
- 70-84分：较为匹配，推荐面试
- 55-69分：基本匹配，可以考虑
- 40-54分：匹配度一般，谨慎考虑
- 0-39分：不太匹配，不推荐

【输出格式】
请严格按照以下JSON格式输出（不要包含```json等markdown标记）：
{{
    "match_score": 综合匹配分数,
    "education_score": 学历匹配分数,
    "experience_score": 经验匹配分数,
    "skills_score": 技能匹配分数,
    "education_analysis": "学历匹配的详细分析，说明为什么给这个分数",
    "experience_analysis": "工作经验匹配的详细分析，包括年限、相关性、项目经验等",
    "skills_analysis": "技能匹配的详细分析，列出匹配的技能和缺失的技能",
    "match_analysis": "综合匹配分析，客观评价候选人的整体适配度",
    "strengths": ["具体优势1", "具体优势2", "具体优势3"],
    "weaknesses": ["具体不足1", "具体不足2"],
    "interview_suggestions": "具体的面试建议和考察重点",
    "hr_recommendation": "明确的招聘建议"
}}

【关键要求】
1. **评分要客观务实**：不要轻易给满分或极低分，大部分情况应该在50-85分区间
2. **分数必须有依据**：每个分数都要在分析中给出理由
3. **避免极端评分**：除非特别突出或特别差，否则不要给90+或20-
4. **工作年限要准确判断**：如果年限达标，经验分不应低于60分
5. **技能要逐项对比**：仔细对比候选人的技能清单和岗位要求
6. **综合分数要合理**：确保综合分数是加权平均的结果
7. **必须是纯JSON**：不要添加任何说明文字或markdown格式
"""

        try:
            print(f"[AI匹配] 开始匹配 {resume.name} -> {job.title}")

            messages = [
                {'role': 'system', 'content': '你是一位资深的HR专家和人才评估顾问，擅长客观公正地评估候选人与岗位的匹配度。'},
                {'role': 'user', 'content': prompt}
            ]
            response = DeepSeekClient.send_request(
                messages=messages,
                temperature=0.2, # 匹配任务需要稳定，所以温度低
                timeout=45,
                max_tokens=2000
            )

            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']

                print(f"[AI匹配] API响应成功，内容长度: {len(content)}")

                # 提取JSON（更健壮的提取方式）
                # 先尝试清理markdown代码块标记
                content_clean = content.strip()
                if content_clean.startswith('```'):
                    # 移除开头的```json或```
                    content_clean = re.sub(r'^```(?:json)?\s*', '', content_clean)
                    # 移除结尾的```
                    content_clean = re.sub(r'```\s*$', '', content_clean)

                # 提取JSON
                json_match = re.search(r'\{[\s\S]*\}', content_clean)
                if json_match:
                    match_data = json.loads(json_match.group())

                    print(f"[AI匹配] 解析成功，综合分数: {match_data.get('match_score', 0)}")

                    # ===== 分数合理性验证和修正 =====
                    education_score = float(match_data.get('education_score', 0))
                    experience_score = float(match_data.get('experience_score', 0))
                    skills_score = float(match_data.get('skills_score', 0))

                    # 1. 工作年限验证 - 如果候选人年限>=要求，经验分不应低于60分
                    if resume.work_years >= job.work_years_required and experience_score < 60:
                        print(
                            f"[AI匹配] 修正：候选人工作{resume.work_years}年 >= 要求{job.work_years_required}年，经验分从{experience_score}调整为70")
                        experience_score = 70.0
                        match_data['experience_score'] = 70.0
                        match_data[
                            'experience_analysis'] += f"\n\n【系统修正】候选人工作年限{resume.work_years}年达到岗位要求{job.work_years_required}年，基础分调整为70分。"

                    # 2. 学历验证 - 避免给满分
                    if education_score >= 95:
                        print(f"[AI匹配] 修正：学历分{education_score}过高，调整为85")
                        education_score = 85.0
                        match_data['education_score'] = 85.0

                    # 3. 重新计算综合分数（使用权重）
                    calculated_score = (
                            education_score * education_weight +
                            experience_score * experience_weight +
                            skills_score * skills_weight
                    )

                    # 如果AI给的综合分与计算结果相差太大，使用计算结果
                    ai_match_score = float(match_data.get('match_score', 0))
                    if abs(calculated_score - ai_match_score) > 10:
                        print(f"[AI匹配] 修正：综合分从{ai_match_score}调整为{calculated_score:.1f}（加权计算）")
                        match_data['match_score'] = round(calculated_score, 1)
                    else:
                        match_data['match_score'] = round(ai_match_score, 1)

                    print(
                        f"[AI匹配] 最终分数 - 学历:{education_score} 经验:{experience_score} 技能:{skills_score} 综合:{match_data['match_score']}")

                    # 构建详细的分析文本
                    detailed_analysis = f"""
【学历匹配分析】（{match_data.get('education_score', 0)}分）
{match_data.get('education_analysis', '无')}

【工作经验分析】（{match_data.get('experience_score', 0)}分）
{match_data.get('experience_analysis', '无')}

【技能匹配分析】（{match_data.get('skills_score', 0)}分）
{match_data.get('skills_analysis', '无')}

【综合评价】
{match_data.get('match_analysis', '无')}

【候选人优势】
{chr(10).join(['• ' + s for s in match_data.get('strengths', [])])}

【需要关注的点】
{chr(10).join(['• ' + w for w in match_data.get('weaknesses', [])])}
"""

                    interview_suggestions = f"""
【面试建议】
{match_data.get('interview_suggestions', '无')}

【HR招聘建议】
{match_data.get('hr_recommendation', '无')}
"""

                    # 创建或更新匹配结果
                    match_result, created = MatchResult.objects.update_or_create(
                        job=job,
                        resume=resume,
                        defaults={
                            'match_score': float(match_data.get('match_score', 0)),
                            'education_score': float(match_data.get('education_score', 0)),
                            'experience_score': float(match_data.get('experience_score', 0)),
                            'skills_score': float(match_data.get('skills_score', 0)),
                            'match_analysis': detailed_analysis.strip(),
                            'interview_suggestions': interview_suggestions.strip(),
                        }
                    )

                    action = "创建" if created else "更新"
                    print(f"[AI匹配] {action}匹配结果成功")

                    return match_result
                else:
                    print(f"[AI匹配] 未找到JSON数据，响应内容: {content[:200]}")
                    return None
            else:
                print(f"[AI匹配] API调用失败: {response.status_code}, {response.text[:200]}")
                return None

        except json.JSONDecodeError as e:
            print(f"[AI匹配] JSON解析错误: {e}")
            print(f"[AI匹配] 原始内容: {content[:500] if 'content' in locals() else '无'}")
            return None
        except requests.exceptions.Timeout:
            print(f"[AI匹配] 请求超时")
            return None
        except Exception as e:
            print(f"[AI匹配] 匹配错误: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return None

    @staticmethod
    def batch_match(job):
        """批量匹配简历到岗位"""
        # 获取所有已解析的简历
        resumes = Resume.objects.filter(status='parsed')

        match_results = []
        for resume in resumes:
            result = JobMatchService.match_resume_to_job(resume, job)
            if result:
                match_results.append(result)

        return match_results

    @staticmethod
    def get_match_statistics(job):
        """获取匹配统计数据"""
        all_matches = MatchResult.objects.filter(job=job)

        if not all_matches.exists():
            return None

        total_count = all_matches.count()
        excellent_count = all_matches.filter(match_score__gte=80).count()  # 优秀
        good_count = all_matches.filter(match_score__gte=60, match_score__lt=80).count()  # 良好
        fair_count = all_matches.filter(match_score__gte=40, match_score__lt=60).count()  # 一般
        poor_count = all_matches.filter(match_score__lt=40).count()  # 较差

        # 平均分
        avg_score = sum([m.match_score for m in all_matches]) / total_count

        # 学历分布
        education_dist = {}
        for match in all_matches:
            edu = match.resume.education or '未知'
            education_dist[edu] = education_dist.get(edu, 0) + 1

        return {
            'total_count': total_count,
            'excellent_count': excellent_count,
            'good_count': good_count,
            'fair_count': fair_count,
            'poor_count': poor_count,
            'avg_score': round(avg_score, 2),
            'education_distribution': education_dist,
        }

    @staticmethod
    def match_jobs_for_resume(resume):
        """为简历匹配所有活跃岗位（求职者视角）"""
        if resume.status != 'parsed' or not resume.parsed_data:
            return []

        # 获取所有活跃的岗位
        active_jobs = Job.objects.filter(is_active=True)

        match_results = []
        for job in active_jobs:
            result = JobMatchService.match_resume_to_job(resume, job)
            if result:
                match_results.append(result)

        return match_results