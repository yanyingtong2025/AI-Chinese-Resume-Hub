"""
简历解析服务
"""
from django.conf import settings
import requests
import PyPDF2
import docx
import json
import re


class DeepSeekClient:
    """底层客户端：只负责把请求发出去，不处理业务逻辑"""

    @staticmethod
    def send_request(messages, temperature=0.7, timeout=60, max_tokens=None):
        # 统一配置请求头和基础 URL
        headers = {
            'Authorization': f'Bearer {settings.DEEPSEEK_API_KEY}',
            'Content-Type': 'application/json'
        }
        payload = {
            'model': 'deepseek-chat',
            'messages': messages,
            'temperature': temperature
        }

        if max_tokens:
            payload['max_tokens'] = max_tokens

        # 不写 try...except，让异常往上抛，交给具体的业务去捕获
        response = requests.post(
            settings.DEEPSEEK_API_URL,
            headers=headers,
            json=payload,
            timeout=timeout
        )
        return response


class ResumeParserService:
    """简历解析服务类"""

    @staticmethod
    def extract_text_from_pdf(file_path):
        """从PDF提取文本"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ''
                for page in pdf_reader.pages:
                    text += page.extract_text()
                return text
        except Exception as e:
            print(f"PDF解析错误: {e}")
            return None

    @staticmethod
    def extract_text_from_docx(file_path):
        """从Word文档提取文本"""
        try:
            print(f"[解析Word] 开始读取文件: {file_path}")
            doc = docx.Document(file_path)
            paragraphs = doc.paragraphs
            print(f"[解析Word] 文档有 {len(paragraphs)} 个段落")
            text = '\n'.join([paragraph.text for paragraph in paragraphs])
            print(f"[解析Word] 提取文本成功，长度: {len(text)}")
            return text
        except Exception as e:
            print(f"[解析Word] 错误: {e}")
            import traceback
            traceback.print_exc()
            return None

    @staticmethod
    def extract_text(file_path):
        """根据文件类型提取文本"""
        if file_path.endswith('.pdf'):
            return ResumeParserService.extract_text_from_pdf(file_path)
        elif file_path.endswith('.docx') or file_path.endswith('.doc'):
            return ResumeParserService.extract_text_from_docx(file_path)
        else:
            return None

    @staticmethod
    def parse_with_ai(text):
        """使用DeepSeek AI解析简历"""
        prompt = f"""请从以下简历文本中提取结构化信息，并以JSON格式返回。

简历文本：
{text}

请提取以下信息（如果文本中没有，字段值为空字符串或null）：
1. 基本信息：姓名、性别、年龄、电话、邮箱
2. 教育背景：学历、毕业院校、专业、毕业时间
3. 工作经历：公司名称、职位、工作时间、工作内容（数组形式）
4. 项目经验：项目名称、项目描述、使用技术、个人职责（数组形式）
5. 技能特长：技能列表（数组形式）
6. 工作年限：根据工作经历计算

返回格式（纯JSON，不要包含任何其他文字）：
{{
    "name": "姓名",
    "gender": "性别",
    "age": 年龄,
    "phone": "电话",
    "email": "邮箱",
    "education": "学历",
    "school": "毕业院校",
    "major": "专业",
    "graduation_time": "毕业时间",
    "work_years": 工作年限,
    "work_experience": [
        {{
            "company": "公司名称",
            "position": "职位",
            "duration": "工作时间",
            "description": "工作内容"
        }}
    ],
    "projects": [
        {{
            "name": "项目名称",
            "description": "项目描述",
            "technologies": "使用技术",
            "role": "个人职责"
        }}
    ],
    "skills": ["技能1", "技能2"]
}}
"""

        try:
            import time
            start_time = time.time()
            print(f"[AI解析] 开始调用DeepSeek API...")
            print(f"[AI解析] 简历文本长度: {len(text)} 字符")

            messages=[{'role': 'user', 'content': prompt}]
            response = DeepSeekClient.send_request(messages, temperature=0.3,timeout=45)

            elapsed = time.time() - start_time
            print(f"[AI解析] API响应时间: {elapsed:.2f}秒")

            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']

                # 提取JSON部分
                json_match = re.search(r'\{[\s\S]*\}', content)
                if json_match:
                    json_str = json_match.group()
                    parsed_data = json.loads(json_str)
                    return parsed_data
                else:
                    print("未找到JSON数据")
                    return None
            else:
                print(f"API调用失败: {response.status_code}, {response.text}")
                return None

        except Exception as e:
            print(f"AI解析错误: {e}")
            return None

    @staticmethod
    def calculate_resume_score(resume_text, parsed_data):
        """计算简历评分（基于规则和AI评估）"""
        if not resume_text or not parsed_data:
            return 0, {}

        score_details = {}
        total_score = 0

        # 1. 基本信息完整度 (20分)
        basic_info_score = 0
        required_fields = ['name', 'phone', 'email', 'education', 'school', 'major']
        for field in required_fields:
            if parsed_data.get(field):
                basic_info_score += 3.33
        score_details['基本信息完整度'] = round(basic_info_score, 1)
        total_score += basic_info_score

        # 2. 工作经历质量 (25分)
        work_exp_score = 0
        work_experience = parsed_data.get('work_experience', [])
        if work_experience:
            # 有工作经历基础分10分
            work_exp_score = 10
            # 每段经历描述超过50字加3分，最多15分
            for exp in work_experience[:5]:
                if exp.get('description') and len(exp['description']) > 50:
                    work_exp_score += 3
            work_exp_score = min(work_exp_score, 25)
        score_details['工作经历质量'] = round(work_exp_score, 1)
        total_score += work_exp_score

        # 3. 项目经验 (20分)
        project_score = 0
        projects = parsed_data.get('projects', [])
        if projects:
            # 有项目经验基础分8分
            project_score = 8
            # 每个项目有详细描述加4分，最多12分
            for proj in projects[:3]:
                if proj.get('description') and len(proj['description']) > 50:
                    project_score += 4
            project_score = min(project_score, 20)
        score_details['项目经验'] = round(project_score, 1)
        total_score += project_score

        # 4. 技能特长 (15分)
        skills_score = 0
        skills = parsed_data.get('skills', [])
        if skills:
            # 技能数量评分
            skill_count = len(skills)
            if skill_count >= 8:
                skills_score = 15
            elif skill_count >= 5:
                skills_score = 12
            elif skill_count >= 3:
                skills_score = 8
            else:
                skills_score = 5
        score_details['技能特长'] = round(skills_score, 1)
        total_score += skills_score

        # 5. 简历长度和内容丰富度 (10分)
        content_score = 0
        text_length = len(resume_text)
        if text_length >= 1500:
            content_score = 10
        elif text_length >= 1000:
            content_score = 8
        elif text_length >= 600:
            content_score = 6
        elif text_length >= 300:
            content_score = 4
        else:
            content_score = 2
        score_details['内容丰富度'] = round(content_score, 1)
        total_score += content_score

        # 6. 教育背景 (10分)
        education_score = 0
        education = parsed_data.get('education', '').lower()
        if '博士' in education or 'phd' in education:
            education_score = 10
        elif '硕士' in education or 'master' in education or '研究生' in education:
            education_score = 9
        elif '本科' in education or 'bachelor' in education or '学士' in education:
            education_score = 8
        elif '专科' in education or '大专' in education:
            education_score = 6
        elif education:
            education_score = 4
        score_details['教育背景'] = round(education_score, 1)
        total_score += education_score

        # 确保总分不超过100
        total_score = min(total_score, 100)

        return round(total_score, 1), score_details

    @staticmethod
    def optimize_resume(resume_text, job_description=None):
        """生成简历优化建议"""
        # 检查输入
        if not resume_text or len(resume_text.strip()) < 50:
            return "简历内容太少，无法生成有效建议。请上传完整的简历。"

        if job_description:
            prompt = f"""作为专业的HR顾问，请分析以下简历，并针对目标岗位提供优化建议。

简历内容：
{resume_text[:2000]}

目标岗位描述：
{job_description}

请提供：
1. 简历的优点
2. 需要改进的地方
3. 针对目标岗位的具体优化建议
4. 关键词优化建议

请用中文回答，分点列出。"""
        else:
            prompt = f"""作为专业的HR顾问，请分析以下简历，并提供优化建议。

简历内容：
{resume_text[:2000]}

请提供：
1. 简历的优点（2-3点）
2. 需要改进的地方（3-4点）
3. 格式和内容优化建议（2-3点）
4. 如何提升简历吸引力（2-3点）

请用中文回答，分点列出，简洁明了。"""

        try:
            print(f"[优化建议] 开始调用API...")
            print(f"[优化建议] API URL: {settings.DEEPSEEK_API_URL}")
            print(f"[优化建议] 简历长度: {len(resume_text)}")

            messages=[{'role': 'user', 'content': prompt}]
            response = DeepSeekClient.send_request(messages)

            print(f"[优化建议] API响应状态: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                suggestions = result['choices'][0]['message']['content']
                print(f"[优化建议] 成功生成建议，长度: {len(suggestions)}")
                return suggestions
            else:
                error_msg = f"API返回错误 (状态码: {response.status_code})"
                print(f"[优化建议] {error_msg}")
                print(f"[优化建议] 响应内容: {response.text[:200]}")

                # 返回更详细的错误信息
                return f"""优化建议生成失败

错误信息：{error_msg}

可能原因：
1. API密钥配置错误
2. API服务暂时不可用
3. 网络连接问题

建议：
- 检查 settings.py 中的 DEEPSEEK_API_KEY 配置
- 确认网络连接正常
- 稍后重试"""

        except requests.exceptions.Timeout:
            print(f"[优化建议] API请求超时")
            return """优化建议生成失败

错误：请求超时

建议：
- 请稍后重试
- 如果问题持续，请检查网络连接"""

        except requests.exceptions.ConnectionError:
            print(f"[优化建议] 网络连接错误")
            return """优化建议生成失败

错误：无法连接到API服务

建议：
- 检查网络连接
- 确认防火墙设置
- 稍后重试"""

        except Exception as e:
            print(f"[优化建议] 未知错误: {type(e).__name__}: {e}")
            return f"""优化建议生成失败

错误类型：{type(e).__name__}
错误详情：{str(e)}

建议：
- 检查系统配置
- 查看日志文件
- 联系技术支持"""

    @staticmethod
    def generate_optimized_resume_content(original_resume_text, optimization_suggestions, parsed_data):
        """根据优化建议生成新的简历内容"""
        print(f"[生成优化简历] 开始生成...")

        prompt = f"""作为专业的简历顾问，请根据原简历内容和优化建议，重新生成一份优化后的简历内容。

原简历内容：
{original_resume_text[:2000]}

优化建议：
{optimization_suggestions[:1000]}

要求：
1. 保留所有真实信息（姓名、联系方式、学历、工作经历等）
2. 根据优化建议改进描述方式和表达
3. 突出核心竞争力和亮点
4. 使用更专业的表达方式
5. 优化项目经验和技能描述
6. 添加量化数据和成果展示

请直接输出优化后的简历全文，保持结构化格式，包含：
- 基本信息
- 教育背景  
- 工作经历
- 项目经验
- 技能特长
- 个人优势

直接输出简历内容，不要有任何前缀说明。"""

        try:
            messages=[{'role': 'user', 'content': prompt}]
            response = DeepSeekClient.send_request(messages, timeout=90)

            if response.status_code == 200:
                result = response.json()
                optimized_content = result['choices'][0]['message']['content']
                print(f"[生成优化简历] 成功，长度: {len(optimized_content)}")
                return optimized_content
            else:
                print(f"[生成优化简历] API错误: {response.status_code}")
                return None

        except Exception as e:
            print(f"[生成优化简历] 错误: {type(e).__name__}: {e}")
            return None

