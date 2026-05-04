# API 完整文档 (API Documentation)

智能简历筛选系统的完整 API 参考文档。

---

## 📋 快速导航

- [认证相关](#认证相关-authentication)
- [简历管理](#简历管理-resumes)
- [岗位管理](#岗位管理-jobs)
- [投递管理](#投递管理-applications)
- [匹配结果](#匹配结果-match-results)
- [通用响应](#通用响应-responses)
- [错误处理](#错误处理-error-handling)

---

## 认证相关 (Authentication)

### 用户注册

**端点：** `POST /users/register/`

**请求体：**
```json
{
    "username": "string",           // 用户名 (3-150 字符)
    "email": "string",              // 邮箱 (有效的邮箱格式)
    "password": "string",           // 密码 (至少 8 字符)
    "password_confirm": "string",   // 确认密码 (必须与 password 一致)
    "role": "string"                // 角色: "jobseeker" 或 "hr"
}
```

**响应 (201 Created)：**
```json
{
    "id": 1,
    "username": "zhangsan",
    "email": "zhangsan@example.com",
    "role": "jobseeker",
    "message": "注册成功，请登录"
}
```

**错误响应 (400 Bad Request)：**
```json
{
    "errors": {
        "username": ["用户名已存在"],
        "email": ["邮箱格式不正确"],
        "password": ["密码过于简单"]
    }
}
```

---

### 用户登录

**端点：** `POST /users/login/`

**请求体：**
```json
{
    "username": "string",           // 用户名
    "password": "string"            // 密码
}
```

**响应 (200 OK)：**
```json
{
    "id": 1,
    "username": "zhangsan",
    "email": "zhangsan@example.com",
    "role": "jobseeker",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "message": "登录成功"
}
```

**错误响应 (401 Unauthorized)：**
```json
{
    "error": "用户名或密码错误"
}
```

---

### 获取当前用户信息

**端点：** `GET /users/profile/`

**请求头：**
```
Authorization: Bearer <token>
```

**响应 (200 OK)：**
```json
{
    "id": 1,
    "username": "zhangsan",
    "email": "zhangsan@example.com",
    "role": "jobseeker",
    "created_at": "2026-01-15T10:30:00Z"
}
```

---

## 简历管理 (Resumes)

### 上传简历

**端点：** `POST /resumes/upload/`

**请求头：**
```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**请求体：**
```
file: <binary file>             // PDF 或 DOCX 文件 (最大 50MB)
```

**响应 (201 Created)：**
```json
{
    "id": 1,
    "file_name": "resume.pdf",
    "status": "pending",
    "created_at": "2026-01-15T10:30:00Z",
    "message": "简历已上传，处理中，请稍候..."
}
```

**错误响应 (400 Bad Request)：**
```json
{
    "error": "不支持的文件格式，请上传 PDF 或 DOCX 文件"
}
```

---

### 获取简历列表

**端点：** `GET /resumes/list/`

**请求头：**
```
Authorization: Bearer <token>
```

**查询参数：**
```
page=int                        // 页码 (默认: 1)
per_page=int                    // 每页数量 (默认: 10)
status=string                   // 筛选状态: pending/parsed/failed
```

**响应 (200 OK)：**
```json
{
    "total": 5,
    "page": 1,
    "per_page": 10,
    "resumes": [
        {
            "id": 1,
            "file_name": "resume.pdf",
            "status": "parsed",
            "score": 82.5,
            "created_at": "2026-01-15T10:30:00Z",
            "updated_at": "2026-01-15T10:35:00Z"
        }
    ]
}
```

---

### 获取简历详情（含评分）

**端点：** `GET /resumes/detail/<id>/`

**请求头：**
```
Authorization: Bearer <token>
```

**响应 (200 OK)：**
```json
{
    "id": 1,
    "file_name": "resume.pdf",
    "name": "张三",
    "email": "zhangsan@example.com",
    "phone": "13800138000",
    "education": "本科",
    "school": "清华大学",
    "major": "计算机科学与技术",
    "work_years": 5,
    "status": "parsed",
    
    "score": 82.5,
    "score_details": {
        "education": {
            "score": 75,
            "feedback": "本科学历满足大多数岗位需求"
        },
        "experience": {
            "score": 85,
            "feedback": "5 年工作经验，经历包括初创公司和大厂"
        },
        "projects": {
            "score": 80,
            "feedback": "3 个项目经验，技术栈覆盖全面"
        },
        "skills": {
            "score": 88,
            "feedback": "技能清单完整，包含多个技术栈"
        },
        "content_quality": {
            "score": 78,
            "feedback": "表达清晰，但可增加量化数据"
        },
        "competitiveness": {
            "score": 72,
            "feedback": "市场竞争力中等，建议补充亮点项目"
        }
    },
    
    "optimization_suggestions": [
        {
            "dimension": "projects",
            "priority": "high",
            "suggestion": "增加 2-3 个产品级项目经验，特别是带有量化成果的项目"
        },
        {
            "dimension": "content_quality",
            "priority": "medium",
            "suggestion": "补充具体的数字化成就，如 '用户数增长 50%' 等"
        }
    ],
    
    "parsed_data": {
        "work_experience": [
            {
                "company": "字节跳动",
                "position": "高级后端工程师",
                "duration": "2023-01 至 2026-01",
                "description": "负责推荐系统核心模块开发..."
            }
        ],
        "projects": [
            {
                "name": "AI 简历筛选系统",
                "description": "使用 Django + DeepSeek AI 构建的智能简历筛选平台",
                "technologies": "Python, Django, DeepSeek API, MySQL",
                "role": "技术负责人"
            }
        ],
        "skills": ["Python", "Django", "MySQL", "Redis", "Docker"]
    },
    
    "created_at": "2026-01-15T10:30:00Z",
    "updated_at": "2026-01-15T10:35:00Z"
}
```

**错误响应 (404 Not Found)：**
```json
{
    "error": "简历不存在"
}
```

---

### 编辑简历信息（元数据）

**端点：** `PATCH /resumes/edit/<id>/`

**请求头：**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**请求体：** (所有字段可选)
```json
{
    "name": "string",
    "email": "string",
    "phone": "string",
    "education": "string",
    "school": "string",
    "major": "string",
    "work_years": "integer"
}
```

**响应 (200 OK)：**
```json
{
    "id": 1,
    "message": "简历信息已更新"
}
```

---

### 删除简历

**端点：** `DELETE /resumes/delete/<id>/`

**请求头：**
```
Authorization: Bearer <token>
```

**响应 (200 OK)：**
```json
{
    "message": "简历已删除"
}
```

---

## 岗位管理 (Jobs)

### 发布岗位

**端点：** `POST /jobs/create/`

**请求头：**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**请求体：**
```json
{
    "title": "string",                      // 岗位名称 (必填)
    "company": "string",                    // 公司名称 (必填)
    "department": "string",                 // 部门 (可选)
    "location": "string",                   // 工作地点 (必填)
    "salary_min": "integer",                // 最低薪资 K (可选)
    "salary_max": "integer",                // 最高薪资 K (可选)
    
    "education_required": "string",         // 学历要求: "大专", "本科", "硕士" 等
    "work_years_required": "integer",       // 工作年限要求
    "skills_required": "string",            // 技能要求 (逗号分隔): "Python,Django,MySQL"
    "job_description": "string",            // 岗位描述
    "job_requirements": "string",           // 任职要求
    
    "education_weight": "float",            // 学历权重 0.0-1.0 (默认: 0.25)
    "experience_weight": "float",           // 经验权重 0.0-1.0 (默认: 0.40)
    "skills_weight": "float"                // 技能权重 0.0-1.0 (默认: 0.35)
}
```

**响应 (201 Created)：**
```json
{
    "id": 1,
    "title": "Python 开发工程师",
    "company": "字节跳动",
    "message": "岗位已发布，开始匹配..."
}
```

**错误响应 (400 Bad Request)：**
```json
{
    "errors": {
        "title": ["岗位名称不能为空"],
        "skills_required": ["权重之和必须为 1.0"]
    }
}
```

---

### 获取岗位列表

**端点：** `GET /jobs/list/`

**查询参数：**
```
page=int                        // 页码
per_page=int                    // 每页数量
search=string                   // 搜索岗位名称
is_active=boolean               // 筛选活跃岗位
```

**响应 (200 OK)：**
```json
{
    "total": 20,
    "page": 1,
    "per_page": 10,
    "jobs": [
        {
            "id": 1,
            "title": "Python 开发工程师",
            "company": "字节跳动",
            "location": "北京",
            "salary_min": 25,
            "salary_max": 35,
            "work_years_required": 3,
            "skills_required": "Python,Django,MySQL",
            "created_at": "2026-01-15T10:30:00Z",
            "application_count": 15,
            "match_count": 8
        }
    ]
}
```

---

### 获取岗位详情

**端点：** `GET /jobs/detail/<id>/`

**响应 (200 OK)：**
```json
{
    "id": 1,
    "title": "Python 开发工程师",
    "company": "字节跳动",
    "department": "后端架构部",
    "location": "北京",
    "salary_min": 25,
    "salary_max": 35,
    
    "education_required": "本科",
    "work_years_required": 3,
    "skills_required": "Python,Django,MySQL,Redis,Docker",
    "job_description": "...",
    "job_requirements": "...",
    
    "education_weight": 0.25,
    "experience_weight": 0.40,
    "skills_weight": 0.35,
    
    "is_active": true,
    "created_at": "2026-01-15T10:30:00Z",
    "updated_at": "2026-01-15T10:30:00Z"
}
```

---

### 编辑岗位

**端点：** `PATCH /jobs/edit/<id>/`

**请求头：**
```
Authorization: Bearer <token>
```

**请求体：** (所有字段可选)
```json
{
    "title": "string",
    "job_description": "string",
    "salary_min": "integer",
    "salary_max": "integer",
    "is_active": "boolean"
}
```

**响应 (200 OK)：**
```json
{
    "message": "岗位已更新"
}
```

---

### 删除岗位

**端点：** `DELETE /jobs/delete/<id>/`

**响应 (200 OK)：**
```json
{
    "message": "岗位已删除"
}
```

---

## 投递管理 (Applications)

### 投递简历到岗位

**端点：** `POST /jobs/apply/`

**请求头：**
```
Authorization: Bearer <token>
```

**请求体：**
```json
{
    "job_id": "integer",
    "resume_id": "integer"
}
```

**响应 (201 Created)：**
```json
{
    "id": 1,
    "job_id": 1,
    "resume_id": 1,
    "status": "pending",
    "created_at": "2026-01-15T10:30:00Z",
    "message": "投递成功"
}
```

**错误响应 (409 Conflict)：**
```json
{
    "error": "已投递过该岗位"
}
```

---

### 获取我的投递列表

**端点：** `GET /jobs/my_applications/`

**请求头：**
```
Authorization: Bearer <token>
```

**查询参数：**
```
status=string               // 筛选状态: pending/viewed/interested/interview/rejected
sort_by=string             // 排序: created_at/-created_at
```

**响应 (200 OK)：**
```json
{
    "total": 10,
    "applications": [
        {
            "id": 1,
            "job": {
                "id": 1,
                "title": "Python 开发工程师",
                "company": "字节跳动"
            },
            "resume": {
                "id": 1,
                "file_name": "resume.pdf",
                "score": 82.5
            },
            "status": "pending",
            "created_at": "2026-01-15T10:30:00Z",
            "viewed_at": null
        }
    ]
}
```

---

### HR 获取岗位的投递列表

**端点：** `GET /jobs/<job_id>/applications/`

**请求头：**
```
Authorization: Bearer <token>
```

**查询参数：**
```
status=string               // 筛选状态
sort_by=string             // 排序: match_score/-match_score/created_at
page=int
per_page=int
```

**响应 (200 OK)：**
```json
{
    "total": 25,
    "job": {
        "id": 1,
        "title": "Python 开发工程师"
    },
    "applications": [
        {
            "id": 1,
            "jobseeker": {
                "id": 1,
                "username": "zhangsan"
            },
            "resume": {
                "id": 1,
                "name": "张三",
                "score": 82.5
            },
            "status": "pending",
            "match_score": 88.5,
            "created_at": "2026-01-15T10:30:00Z",
            "viewed_at": null
        }
    ]
}
```

---

### 更新投递状态

**端点：** `PATCH /jobs/applications/<id>/status/`

**请求头：**
```
Authorization: Bearer <token>
```

**请求体：**
```json
{
    "status": "string",     // pending/viewed/interested/interview/rejected
    "hr_notes": "string"    // (可选) HR 备注
}
```

**响应 (200 OK)：**
```json
{
    "id": 1,
    "status": "interview",
    "message": "状态已更新，已邀请面试"
}
```

---

## 匹配结果 (Match Results)

### 获取简历的推荐岗位

**端点：** `GET /resumes/<resume_id>/recommendations/`

**请求头：**
```
Authorization: Bearer <token>
```

**查询参数：**
```
min_score=float             // 最低匹配分数 (默认: 60.0)
limit=int                   // 返回数量 (默认: 10)
```

**响应 (200 OK)：**
```json
{
    "resume": {
        "id": 1,
        "name": "张三",
        "score": 82.5
    },
    "recommendations": [
        {
            "id": 1,
            "job": {
                "id": 1,
                "title": "Python 开发工程师",
                "company": "字节跳动",
                "location": "北京",
                "salary_min": 25,
                "salary_max": 35
            },
            "match_score": 88.5,
            "match_analysis": {
                "education_match": {
                    "score": 90,
                    "feedback": "学历完全符合"
                },
                "experience_match": {
                    "score": 85,
                    "feedback": "经验相关"
                },
                "skills_match": {
                    "score": 88,
                    "feedback": "技能匹配度高"
                }
            }
        }
    ]
}
```

---

### 获取岗位的匹配候选人

**端点：** `GET /jobs/<job_id>/matches/`

**请求头：**
```
Authorization: Bearer <token>
```

**查询参数：**
```
min_score=float             // 最低匹配分数
limit=int                   // 返回数量
sort_by=string             // 排序: -match_score/created_at
```

**响应 (200 OK)：**
```json
{
    "job": {
        "id": 1,
        "title": "Python 开发工程师"
    },
    "matches": [
        {
            "id": 1,
            "resume": {
                "id": 1,
                "name": "张三",
                "score": 82.5
            },
            "candidate": {
                "id": 1,
                "username": "zhangsan",
                "email": "zhangsan@example.com"
            },
            "match_score": 88.5,
            "match_analysis": "..."
        }
    ]
}
```

---

## 通用响应 (Responses)

### 成功响应格式

```json
{
    "data": {},                     // 响应数据
    "message": "string",            // 成功消息 (可选)
    "timestamp": "2026-01-15T10:30:00Z"
}
```

### 分页响应格式

```json
{
    "data": [],
    "pagination": {
        "total": 100,
        "page": 1,
        "per_page": 10,
        "pages": 10,
        "has_prev": false,
        "has_next": true
    }
}
```

---

## 错误处理 (Error Handling)

### HTTP 状态码

| 状态码 | 含义 | 说明 |
|--------|------|------|
| 200 | OK | 请求成功 |
| 201 | Created | 资源创建成功 |
| 400 | Bad Request | 请求参数错误 |
| 401 | Unauthorized | 未授权，需要登录 |
| 403 | Forbidden | 禁止访问，权限不足 |
| 404 | Not Found | 资源不存在 |
| 409 | Conflict | 冲突（如重复投递） |
| 429 | Too Many Requests | 请求过于频繁 |
| 500 | Internal Server Error | 服务器错误 |
| 503 | Service Unavailable | 服务暂时不可用 |

### 错误响应格式

```json
{
    "error": "string",              // 错误信息
    "error_code": "string",         // 错误代码
    "details": {},                  // 详细信息 (可选)
    "timestamp": "2026-01-15T10:30:00Z"
}
```

### 常见错误代码

| 错误代码 | HTTP 状态码 | 说明 |
|---------|-----------|------|
| `UNAUTHORIZED` | 401 | 未授权 |
| `PERMISSION_DENIED` | 403 | 权限不足 |
| `NOT_FOUND` | 404 | 资源不存在 |
| `INVALID_INPUT` | 400 | 输入参数无效 |
| `DUPLICATE_APPLICATION` | 409 | 重复投递 |
| `API_ERROR` | 500 | 外部 API 错误 |
| `DATABASE_ERROR` | 500 | 数据库错误 |
| `RATE_LIMIT_EXCEEDED` | 429 | API 限流 |

---

## 认证方式 (Authentication)

### Bearer Token

```
Authorization: Bearer <jwt_token>
```

### Token 获取

通过登录端点获取：

```bash
curl -X POST http://localhost:8000/users/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "zhangsan",
    "password": "password123"
  }'
```

### Token 刷新

```bash
curl -X POST http://localhost:8000/users/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "<refresh_token>"
  }'
```

---

## 速率限制 (Rate Limiting)

- API 请求限制：每分钟 60 次
- 文件上传限制：每小时 10 个
- AI 调用限制：每天 100 次

超过限制返回 429 Too Many Requests

---

## 注意事项

1. **所有 API 返回均为 JSON 格式**
2. **时间戳采用 ISO 8601 格式**
3. **敏感操作需要授权（Authorization header）**
4. **文件上传大小限制为 50MB**
5. **建议实现 API 请求重试机制处理超时**

---

更多问题？查看 [项目文档](./README.md) 或提交 [Issue](../../issues)
