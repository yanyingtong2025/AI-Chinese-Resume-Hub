# 项目架构文档 (Architecture Documentation)

智能简历筛选系统的完整技术架构设计文档。

---

## 📋 目录 (Table of Contents)

- [系统概述](#系统概述)
- [应用架构](#应用架构)
- [数据流设计](#数据流设计)
- [核心服务](#核心服务)
- [API 设计](#api-设计)
- [扩展方案](#扩展方案)

---

## 系统概述

### 高层架构

```
┌──────────────────────────────────────────────────────────────────┐
│                     用户界面层 (Presentation Layer)              │
│        ┌─────────────┐  ┌──────────────┐  ┌─────────────┐      │
│        │ 求职者界面  │  │  HR 后台     │  │ Admin 管理  │      │
│        └─────────────┘  └──────────────┘  └─────────────┘      │
└──────────────────────────────────────────────────────────────────┘
                                  ↓
┌──────────────────────────────────────────────────────────────────┐
│                    业务逻辑层 (Business Logic Layer)             │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │           Django Framework (MTV Architecture)           │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐    │   │
│  │  │ Users App   │  │ Resumes App │  │ Jobs App     │    │   │
│  │  │ (认证管理)  │  │ (简历管理)  │  │ (岗位&投递) │    │   │
│  │  └─────────────┘  └─────────────┘  └──────────────┘    │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              核心服务层 (Services Layer)                │   │
│  │  ┌──────────────────────────────────────────────────┐   │   │
│  │  │ • ResumeParserService (简历解析)                │   │   │
│  │  │ • JobMatchService (岗位匹配)                    │   │   │
│  │  │ • DeepSeekClient (AI 接口)                    │   │   │
│  │  │ • FileProcessingService (文件处理)             │   │   │
│  │  │ • NotificationService (通知服务)               │   │   │
│  │  └──────────────────────────────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
                                  ↓
┌──────────────────────────────────────────────────────────────────┐
│                    数据访问层 (Data Access Layer)                │
│       ┌─────────────────────────────────────────────────┐       │
│       │   Django ORM (Object-Relational Mapping)       │       │
│       │  • 用户模型 • 简历模型 • 岗位模型 • 投递模型   │       │
│       └─────────────────────────────────────────────────┘       │
└──────────────────────────────────────────────────────────────────┘
                                  ↓
┌──────────────────────────────────────────────────────────────────┐
│                   持久化层 (Persistence Layer)                   │
│       ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│       │   MySQL DB   │  │  File System │  │ Redis Cache  │     │
│       │ (关系数据)   │  │ (简历文件)   │  │  (缓存)      │     │
│       └──────────────┘  └──────────────┘  └──────────────┘     │
└──────────────────────────────────────────────────────────────────┘
                                  ↓
┌──────────────────────────────────────────────────────────────────┐
│                   外部集成 (External Integration)                 │
│       ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│       │ DeepSeek AI  │  │ Email Server │  │ Storage Svc  │     │
│       │   (LLM)      │  │ (通知)       │  │ (文件存储)   │     │
│       └──────────────┘  └──────────────┘  └──────────────┘     │
└──────────────────────────────────────────────────────────────────┘
```

---

## 应用架构

### 项目结构

```
system_demo/
│
├── apps/                           # 应用模块集合
│   ├── users/                      # 用户应用
│   │   ├── __init__.py
│   │   ├── models.py               # User 模型
│   │   ├── views.py                # 登录、注册、仪表板视图
│   │   ├── forms.py                # 用户表单
│   │   ├── urls.py                 # 路由定义
│   │   ├── admin.py                # Admin 配置
│   │   ├── services.py             # 业务逻辑
│   │   ├── tests.py                # 单元测试
│   │   └── migrations/             # 数据库迁移
│   │
│   ├── resumes/                    # 简历应用
│   │   ├── models.py               # Resume、ResumeScore 模型
│   │   ├── views.py                # 简历上传、列表、详情视图
│   │   ├── forms.py                # 简历上传表单
│   │   ├── urls.py                 # 路由定义
│   │   ├── services.py             # ⭐ 简历解析与 AI 评分（核心模块）
│   │   │   ├── ResumeParserService
│   │   │   ├── DeepSeekClient
│   │   │   └── ScoreService
│   │   ├── admin.py                # Admin 配置
│   │   ├── tests.py                # 单元测试
│   │   └── migrations/
│   │
│   ├── jobs/                       # 岗位应用
│   │   ├── models.py               # Job、Application、MatchResult 模型
│   │   ├── views.py                # 岗位列表、投递管理视图
│   │   ├── forms.py                # 岗位表单
│   │   ├── urls.py                 # 路由定义
│   │   ├── services.py             # ⭐ 岗位匹配（核心模块）
│   │   │   ├── JobMatchService
│   │   │   └── MatchScoreService
│   │   ├── admin.py                # Admin 配置
│   │   ├── tests.py                # 单元测试
│   │   └── migrations/
│   │
│   └── __init__.py
│
├── system_demo/                    # 项目配置
│   ├── __init__.py
│   ├── settings.py                 # Django 设置
│   ├── urls.py                     # 主 URL 路由
│   ├── wsgi.py                     # WSGI 应用
│   └── asgi.py                     # ASGI 应用
│
├── templates/                      # HTML 模板
│   ├── base.html                   # 基础模板
│   ├── users/
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── jobseeker_dashboard.html
│   │   └── hr_dashboard.html
│   ├── resumes/
│   │   ├── list.html               # 简历列表
│   │   ├── upload.html             # 简历上传
│   │   ├── detail.html             # 简历详情（含评分）
│   │   └── edit.html
│   └── jobs/
│       ├── list.html               # 岗位列表
│       ├── create.html             # 发布岗位
│       ├── my_applications.html    # 我的投递
│       └── match_results.html      # 匹配结果
│
├── static/                         # 静态资源
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── main.js
│   └── images/
│
├── media/                          # 用户上传文件
│   └── resumes/
│       └── 2026/03/04/             # 按时间戳组织
│
├── manage.py                       # Django 管理脚本
├── requirements.txt                # Python 依赖
├── README.md                       # 中文说明文档
├── README_EN.md                    # 英文说明文档
├── INSTALLATION.md                 # 安装部署指南
├── ARCHITECTURE.md                 # 架构文档（本文件）
├── CONTRIBUTING.md                 # 贡献指南
├── .env.example                    # 环境变量模板
├── .gitignore                      # Git 忽略文件
└── docker-compose.yml              # Docker 编排配置
```

### 应用职责

#### 1. Users App (认证管理)

**职责：**
- 用户注册与登录
- 身份验证与授权
- 用户角色管理（求职者 vs HR）
- 用户信息管理

**关键模型：**
```python
class User(models.Model):
    username = CharField(unique=True)
    email = EmailField(unique=True)
    password = CharField()
    role = CharField(choices=[('jobseeker', '求职者'), ('hr', 'HR')])
    is_active = BooleanField(default=True)
    created_at = DateTimeField(auto_now_add=True)
```

#### 2. Resumes App (简历管理)

**职责：**
- 简历上传与存储
- AI 简历解析
- 6 维度智能评分
- 优化建议生成
- 简历版本管理

**关键模型：**
```python
class Resume(models.Model):
    user = ForeignKey(User)
    file = FileField(upload_to='resumes/%Y/%m/')
    parsed_data = JSONField()        # 结构化信息
    score = FloatField()             # 综合评分
    score_details = JSONField()      # 6 维度详细评分
    optimization_suggestions = TextField()
    status = CharField(choices=[('pending', '待解析'), ('parsed', '已解析')])
```

#### 3. Jobs App (岗位与投递)

**职责：**
- 岗位发布与管理
- 简历投递管理
- 智能岗位匹配
- 投递状态追踪
- HR 候选人管理

**关键模型：**
```python
class Job(models.Model):
    hr_user = ForeignKey(User)
    title = CharField()
    skills_required = TextField()
    job_description = TextField()
    is_active = BooleanField(default=True)

class Application(models.Model):
    job = ForeignKey(Job)
    resume = ForeignKey(Resume)
    jobseeker = ForeignKey(User)
    status = CharField(choices=[...])  # 投递状态流转

class MatchResult(models.Model):
    job = ForeignKey(Job)
    resume = ForeignKey(Resume)
    match_score = FloatField()         # 匹配度
    match_analysis = TextField()       # 匹配分析
```

---

## 数据流设计

### 简历上传与评分流程

```
┌─────────────────────────────────────────────────────────────┐
│  求职者上传简历 (PDF/DOCX)                                 │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│  1. 文件验证与存储                                          │
│  • 检查文件类型和大小                                       │
│  • 保存到 media/resumes/ 目录                              │
│  • 更新 Resume 记录状态为 'pending'                        │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│  2. 文本提取                                                │
│  • PDF: 使用 PyPDF2 提取文本                               │
│  • DOCX: 使用 python-docx 提取文本                         │
│  • 保存原始文本到 Resume.raw_text                          │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│  3. AI 智能解析                                             │
│  • 调用 DeepSeek API 进行深度解析                          │
│  • 提取结构化信息：基本信息、工作经历、项目、技能等        │
│  • 保存到 Resume.parsed_data (JSON)                        │
│  • 状态更新为 'parsed'                                    │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│  4. 6 维度智能评分                                          │
│  • 学历背景评分 (20%)                                       │
│  • 工作经验评分 (25%)                                       │
│  • 项目经验评分 (20%)                                       │
│  • 技能匹配评分 (15%)                                       │
│  • 内容质量评分 (12%)                                       │
│  • 整体竞争力评分 (8%)                                      │
│  • 保存到 Resume.score_details (JSON)                      │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│  5. 优化建议生成                                            │
│  • 分析各维度的薄弱环节                                    │
│  • 生成针对性的改进建议                                    │
│  • 保存到 Resume.optimization_suggestions                 │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│  6. 完成评估，返回结果给求职者                             │
│  • 展示综合评分和 6 维度详细评分                           │
│  • 显示优化建议                                            │
│  • 推荐相关岗位                                            │
└─────────────────────────────────────────────────────────────┘
```

**代码实现流程：**

```python
# 1. 在 views.py 中处理上传
@login_required
def upload_resume(request):
    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            resume = form.save(commit=False)
            resume.user = request.user
            resume.save()
            
            # 异步调用处理管道
            process_resume_async.delay(resume.id)
            
            return redirect('resume_detail', pk=resume.id)

# 2. 在 services.py 中实现处理管道
class ResumeProcessingPipeline:
    @staticmethod
    def process_resume(resume):
        # 步骤 1-2: 文本提取
        text = ResumeParserService.extract_text(resume.file.path)
        resume.raw_text = text
        resume.save()
        
        # 步骤 3: AI 解析
        parsed_data = ResumeParserService.parse_with_ai(text)
        resume.parsed_data = parsed_data
        
        # 步骤 4: 评分
        score_details = ScoreService.calculate_score(parsed_data)
        resume.score_details = score_details
        resume.score = ScoreService.aggregate_score(score_details)
        
        # 步骤 5: 优化建议
        suggestions = ScoreService.generate_suggestions(score_details, parsed_data)
        resume.optimization_suggestions = suggestions
        
        # 标记为已完成
        resume.status = 'parsed'
        resume.save()
```

### 岗位匹配流程

```
┌─────────────────────────────────────────────────────────────┐
│  HR 发布岗位或求职者查看推荐                               │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│  1. 获取匹配候选人池                                        │
│  • 从数据库查询所有已解析的简历                            │
│  • 筛选满足基本条件的候选人                                │
│  │  - 学历 >= 岗位要求                                     │
│  │  - 工作年限 >= 岗位要求                                 │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│  2. 调用 AI 匹配算法                                        │
│  • 对每个候选人进行深度匹配分析                            │
│  • 评估技能匹配度、经验相关性、发展潜力                    │
│  • 生成详细的匹配分析                                      │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│  3. 计算综合匹配分数                                        │
│  • 学历匹配 × education_weight (0.20-0.30)                │
│  • 经验匹配 × experience_weight (0.30-0.50)               │
│  • 技能匹配 × skills_weight (0.20-0.40)                   │
│  • 综合分数 = 学历 + 经验 + 技能                          │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│  4. 排序与筛选                                              │
│  • 按匹配度从高到低排序                                    │
│  • 只展示分数 > 60 的候选人                               │
│  • 返回前 N 个最匹配的候选人                              │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│  5. 缓存与展示                                              │
│  • 保存 MatchResult 记录到数据库                          │
│  • 返回匹配列表给 HR 或求职者                            │
│  • 缓存匹配结果以提高后续查询速度                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 核心服务

### 1. ResumeParserService (简历解析服务)

**功能：**
- 多格式文件解析（PDF、DOCX）
- AI 智能信息提取
- 结构化数据转换

**关键方法：**
```python
class ResumeParserService:
    @staticmethod
    def extract_text(file_path) -> str
        """提取文本内容"""
    
    @staticmethod
    def parse_with_ai(text) -> dict
        """使用 DeepSeek AI 解析简历"""
    
    @staticmethod
    def validate_parsed_data(data) -> bool
        """验证解析结果的有效性"""
```

### 2. JobMatchService (岗位匹配服务)

**功能：**
- 简历与岗位的多维度匹配
- 权重计算与评分
- 匹配结果分析

**关键方法：**
```python
class JobMatchService:
    @staticmethod
    def match_resume_to_job(resume, job) -> MatchResult
        """匹配单个简历到岗位"""
    
    @staticmethod
    def match_job_to_resumes(job) -> List[MatchResult]
        """为岗位匹配所有相关简历"""
    
    @staticmethod
    def calculate_match_score(resume_data, job_req, weights) -> float
        """计算匹配分数"""
```

### 3. DeepSeekClient (AI 客户端)

**功能：**
- 与 DeepSeek API 通信
- 请求/响应管理
- 错误处理与重试

**关键方法：**
```python
class DeepSeekClient:
    @staticmethod
    def send_request(messages, temperature, timeout) -> Response
        """发送请求到 DeepSeek API"""
    
    @staticmethod
    def handle_rate_limit()
        """处理 API 速率限制"""
```

---

## API 设计

### 简历 API

```
# 上传简历
POST /resumes/upload/
Content-Type: multipart/form-data
{
    "file": <binary resume file>
}

Response 201:
{
    "id": 1,
    "status": "pending",
    "message": "简历已上传，处理中..."
}

# 获取简历详情（含评分）
GET /resumes/detail/<id>/

Response 200:
{
    "id": 1,
    "name": "张三",
    "score": 82.5,
    "score_details": {
        "education": 75,
        "experience": 85,
        "projects": 80,
        "skills": 88,
        "content_quality": 78,
        "competitiveness": 72
    },
    "optimization_suggestions": "...",
    "status": "parsed"
}

# 获取推荐岗位
GET /jobs/recommendations/?resume_id=1

Response 200:
{
    "recommendations": [
        {
            "job_id": 1,
            "title": "Python 开发工程师",
            "match_score": 85.5,
            "match_analysis": "..."
        }
    ]
}
```

### 岗位 API

```
# 发布岗位
POST /jobs/create/
{
    "title": "Python 开发工程师",
    "company": "字节跳动",
    "skills_required": "Python, Django, MySQL",
    "education_weight": 0.25,
    "experience_weight": 0.40,
    "skills_weight": 0.35
}

Response 201:
{
    "id": 1,
    "title": "Python 开发工程师",
    "message": "岗位已发布，匹配中..."
}

# 获取匹配候选人
GET /jobs/matches/<id>/

Response 200:
{
    "matches": [
        {
            "resume_id": 1,
            "candidate_name": "张三",
            "match_score": 88.5,
            "match_analysis": "技能完全匹配，经验相关..."
        }
    ]
}
```

---

## 扩展方案

### 1. 异步任务处理

使用 Celery + Redis 处理耗时任务：

```python
# 异步处理简历
@shared_task
def process_resume_async(resume_id):
    resume = Resume.objects.get(id=resume_id)
    ResumeProcessingPipeline.process_resume(resume)

# 异步生成匹配结果
@shared_task
def generate_matches_async(job_id):
    job = Job.objects.get(id=job_id)
    results = JobMatchService.match_job_to_resumes(job)
    for result in results:
        result.save()
```

### 2. 缓存优化

使用 Redis 缓存热点数据：

```python
from django.core.cache import cache

def get_job_matches(job_id):
    cache_key = f'job_matches_{job_id}'
    matches = cache.get(cache_key)
    
    if matches is None:
        matches = MatchResult.objects.filter(job_id=job_id)
        cache.set(cache_key, matches, 3600)  # 缓存 1 小时
    
    return matches
```

### 3. 搜索优化

集成 Elasticsearch 实现全文搜索：

```python
from elasticsearch import Elasticsearch

class ResumeSearchService:
    @staticmethod
    def search_resumes(keyword):
        es = Elasticsearch(['localhost:9200'])
        results = es.search(
            index='resumes',
            body={
                'query': {
                    'multi_match': {
                        'query': keyword,
                        'fields': ['name', 'skills', 'experience']
                    }
                }
            }
        )
        return results
```

### 4. 实时通知

实现 WebSocket 实时推送：

```python
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['user'].id
        await self.channel_layer.group_add(
            f'user_{self.user_id}',
            self.channel_name
        )
        await self.accept()
    
    async def send_notification(self, event):
        await self.send(text_data=json.dumps(event['message']))
```

---

更多细节，请参考代码中的 docstring 和注释！
