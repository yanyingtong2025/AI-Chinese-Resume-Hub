# 贡献指南 (Contributing Guide)

感谢您有兴趣为智能简历筛选系统做贡献！

Thank you for your interest in contributing to the Intelligent Resume Screening System!

## 📋 行为准则 (Code of Conduct)

请遵守以下基本原则：
- 尊重他人的观点和想法
- 提出建设性的反馈
- 专注于对项目最有利的讨论
- 保持友好和包容的态度

## 🐛 报告 Bug (Bug Reports)

如果您发现了 Bug，请创建一个 GitHub Issue，包括：

1. **问题描述** - 清楚地描述问题
2. **复现步骤** - 详细的步骤来复现问题
3. **预期行为** - 应该发生什么
4. **实际行为** - 实际发生了什么
5. **环境信息**：
   - Python 版本
   - Django 版本
   - 操作系统
   - MySQL 版本

## 💡 功能建议 (Feature Requests)

有了新想法？请创建一个 Issue，说明：

1. **功能概述** - 这个功能做什么？
2. **使用场景** - 谁会使用它，为什么？
3. **预期行为** - 如何使用这个功能
4. **可能的实现方式** - 您有什么想法吗？

## 🔧 代码贡献 (Code Contribution)

### 前置步骤

1. **Fork 项目**
   ```bash
   git clone https://github.com/yourusername/system_demo.git
   cd system_demo
   ```

2. **创建虚拟环境**
   ```bash
   python -m venv venv
   source venv/bin/activate  # 或 venv\Scripts\activate (Windows)
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # 开发依赖
   ```

4. **创建特性分支**
   ```bash
   git checkout -b feature/your-feature-name
   ```

### 开发流程

1. **遵循代码风格**
   - 使用 PEP 8 风格指南
   - 最大行长 100 字符
   - 使用类型提示（Python 3.9+）
   - 添加文档字符串

2. **编写代码示例**
   ```python
   def parse_resume(file_path: str) -> dict:
       """
       解析简历文件并提取结构化信息。
       
       Args:
           file_path: 简历文件路径
           
       Returns:
           包含解析数据的字典
           
       Raises:
           FileNotFoundError: 文件不存在时抛出
           ValueError: 文件格式不支持时抛出
       """
       # 实现代码
       pass
   ```

3. **编写测试**
   ```bash
   python manage.py test apps.resumes.tests
   ```

4. **检查代码质量**
   ```bash
   # 运行 linter
   flake8 .
   
   # 检查代码复杂度
   pylint apps/
   ```

### 提交 Pull Request

1. **更新代码**
   ```bash
   git add .
   git commit -m "feat: add resume parsing feature"
   ```

2. **遵循 Commit 规范**
   ```
   feat: 添加新功能
   fix: 修复 bug
   docs: 文档更新
   style: 代码格式调整
   refactor: 代码重构
   test: 添加或更新测试
   chore: 构建脚本、依赖更新等
   ```

3. **推送到 Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

4. **创建 Pull Request**
   - 清楚地说明您的改动
   - 关联相关的 Issue
   - 提供测试证明
   - 确保所有测试都通过

## 📝 文档贡献

### 改进 README
- 修复错别字或不清楚的表述
- 补充缺失的示例
- 改进代码片段的可读性

### 添加教程
- 创建新的 `.md` 文件在 `docs/` 目录
- 包含清晰的标题和代码示例
- 测试所有代码示例
- 包含相关链接

## 🏗️ 项目结构规范

```
system_demo/
├── apps/
│   ├── users/              # 用户应用
│   │   ├── models.py       # 数据模型
│   │   ├── views.py        # 视图函数
│   │   ├── services.py     # 业务逻辑
│   │   ├── forms.py        # 表单定义
│   │   ├── urls.py         # URL 路由
│   │   ├── admin.py        # Django Admin 配置
│   │   └── tests.py        # 单元测试
│   ├── resumes/            # 简历应用
│   └── jobs/               # 岗位应用
├── system_demo/            # 项目配置
│   ├── settings.py         # 全局设置
│   ├── urls.py             # 主 URL 路由
│   └── wsgi.py             # WSGI 配置
├── templates/              # HTML 模板
├── static/                 # 静态资源
├── media/                  # 用户上传文件
├── manage.py               # Django 管理脚本
├── requirements.txt        # 生产依赖
├── requirements-dev.txt    # 开发依赖
└── README.md               # 项目说明
```

## 🧪 测试要求

所有提交的代码必须通过测试：

```bash
# 运行所有测试
python manage.py test

# 运行特定应用的测试
python manage.py test apps.resumes

# 检查测试覆盖率
coverage run --source='.' manage.py test
coverage report
```

## 🔐 安全建议

1. **不要提交敏感信息**
   - API Key、密码等绝不要提交到仓库
   - 使用 `.env` 文件管理敏感配置
   - 确保 `.env` 在 `.gitignore` 中

2. **依赖安全**
   - 定期更新依赖包
   - 检查依赖的安全漏洞
   ```bash
   pip install safety
   safety check
   ```

3. **输入验证**
   - 始终验证用户输入
   - 使用 Django 的内置验证
   - 防止 SQL 注入和 XSS 攻击

## 📚 技术资源

- [Django 官方文档](https://docs.djangoproject.com/)
- [DeepSeek API 文档](https://platform.deepseek.com/api-docs)
- [Python PEP 8 风格指南](https://www.python.org/dev/peps/pep-0008/)
- [Django 最佳实践](https://docs.djangoproject.com/en/4.2/intro/contributing/)

## 🤔 需要帮助？

- 📖 查看项目 [Wiki](../../wiki)
- 💬 在 [GitHub Discussions](../../discussions) 中提问
- 📧 联系维护者 yanyingtong@bupt.edu.cn

## 📄 许可证

通过提交代码，您同意您的贡献将在 MIT 许可证下许可。

---

感谢您的贡献！🎉

Thank you for your contribution!
