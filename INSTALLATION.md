# 安装与部署指南 (Installation & Deployment Guide)

完整的项目安装、配置和部署步骤指南。

---

## 📋 目录 (Table of Contents)

- [系统要求](#系统要求)
- [本地开发环境](#本地开发环境)
- [Docker 部署](#docker-部署)
- [生产环境部署](#生产环境部署)
- [常见问题排查](#常见问题排查)

---

## 系统要求

### 硬件要求

| 资源 | 开发环境 | 生产环境 |
|------|--------|--------|
| CPU | 2 核+ | 4 核+ |
| 内存 | 4GB+ | 8GB+ |
| 硬盘 | 10GB+ SSD | 50GB+ SSD |
| 网络 | 100Mbps+ | 1Gbps+ |

### 软件要求

```
操作系统: Linux (推荐 Ubuntu 20.04+) / Windows 10+ / macOS 11+
Python: 3.9, 3.10, 3.11, 3.12
MySQL: 5.7, 8.0+
Git: 2.20+
```

---

## 本地开发环境

### 第 1 步：安装系统依赖

#### Windows

```powershell
# 安装 Python（https://www.python.org/downloads/）
# 安装 MySQL（https://dev.mysql.com/downloads/mysql/）
# 安装 Git（https://git-scm.com/download/win）

# 验证安装
python --version
mysql --version
git --version
```

#### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install -y python3.10 python3.10-venv python3-pip
sudo apt install -y mysql-server mysql-client
sudo apt install -y git
```

#### macOS

```bash
# 使用 Homebrew
brew install python@3.10
brew install mysql
brew install git

# 验证安装
python3 --version
mysql --version
git --version
```

### 第 2 步：克隆项目

```bash
git clone https://github.com/yourusername/system_demo.git
cd system_demo
```

### 第 3 步：创建虚拟环境

#### Windows

```powershell
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
.\venv\Scripts\activate
```

#### Linux/macOS

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate
```

### 第 4 步：安装 Python 依赖

```bash
# 升级 pip
pip install --upgrade pip

# 安装项目依赖
pip install -r requirements.txt

# 开发依赖（可选）
pip install -r requirements-dev.txt
```

### 第 5 步：配置数据库

#### 创建数据库

```bash
mysql -u root -p
```

```sql
-- 创建数据库
CREATE DATABASE system_demo_db 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- 创建 Django 用户（推荐）
CREATE USER 'django_user'@'localhost' IDENTIFIED BY 'StrongPassword123!@#';
GRANT ALL PRIVILEGES ON system_demo_db.* TO 'django_user'@'localhost';
FLUSH PRIVILEGES;

-- 验证
SHOW GRANTS FOR 'django_user'@'localhost';
EXIT;
```

### 第 6 步：配置环境变量

```bash
# 复制 .env 模板
cp .env.example .env

# 编辑 .env 文件（使用 VSCode、Vim 等编辑器）
# Windows:
# notepad .env

# Linux/macOS:
# nano .env
```

编辑后的 `.env` 示例：

```env
SECRET_KEY=django-insecure-abcd1234efgh5678ijkl9012mnop3456
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

DB_ENGINE=django.db.backends.mysql
DB_NAME=system_demo_db
DB_USER=django_user
DB_PASSWORD=StrongPassword123!@#
DB_HOST=127.0.0.1
DB_PORT=3306

DEEPSEEK_API_KEY=sk-your-real-api-key-here
DEEPSEEK_API_URL=https://api.deepseek.com/chat/completions
DEEPSEEK_API_TIMEOUT=60

MEDIA_URL=/media/
MEDIA_ROOT=media/
```

### 第 7 步：运行数据库迁移

```bash
# 生成迁移文件
python manage.py makemigrations

# 执行迁移
python manage.py migrate

# 验证迁移（应该看到所有应用都是 [X]）
python manage.py showmigrations
```

### 第 8 步：创建超级用户

```bash
python manage.py createsuperuser

# 按提示输入信息：
# Username: admin
# Email: admin@example.com
# Password: (输入强密码)
```

### 第 9 步：创建静态文件

```bash
# 收集静态文件到 staticfiles 目录
python manage.py collectstatic --noinput
```

### 第 10 步：启动开发服务器

```bash
python manage.py runserver 0.0.0.0:8000
```

**访问应用：**
- 首页: http://localhost:8000
- Django Admin: http://localhost:8000/admin
- 用户中心: http://localhost:8000/users
- 简历管理: http://localhost:8000/resumes
- 岗位管理: http://localhost:8000/jobs

---

## Docker 部署

### Dockerfile

创建 `Dockerfile`：

```dockerfile
FROM python:3.10-slim

# 设置时区和语言
ENV TZ=Asia/Shanghai
ENV LANG=C.UTF-8
ENV PYTHONUNBUFFERED=1

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    default-mysql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 复制 requirements
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 收集静态文件
RUN python manage.py collectstatic --noinput

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "system_demo.wsgi:application"]
```

### docker-compose.yml

创建 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  # MySQL 数据库
  db:
    image: mysql:8.0
    container_name: system_demo_db
    environment:
      MYSQL_ROOT_PASSWORD: root_password_123
      MYSQL_DATABASE: system_demo_db
      MYSQL_USER: django_user
      MYSQL_PASSWORD: django_password_123
      TZ: 'Asia/Shanghai'
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Django 应用
  web:
    build: .
    container_name: system_demo_web
    command: >
      sh -c "python manage.py migrate &&
             python manage.py createsuperuser --noinput --username admin --email admin@example.com 2>/dev/null; 
             gunicorn --bind 0.0.0.0:8000 --workers 4 system_demo.wsgi:application"
    ports:
      - "8000:8000"
    volumes:
      - .:/app
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    environment:
      - DEBUG=False
      - SECRET_KEY=your-secret-key
      - DB_ENGINE=django.db.backends.mysql
      - DB_NAME=system_demo_db
      - DB_USER=django_user
      - DB_PASSWORD=django_password_123
      - DB_HOST=db
      - DB_PORT=3306
      - DEEPSEEK_API_KEY=sk-your-key
      - DEEPSEEK_API_URL=https://api.deepseek.com/chat/completions
    depends_on:
      db:
        condition: service_healthy

  # Nginx 反向代理
  nginx:
    image: nginx:alpine
    container_name: system_demo_nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - static_volume:/app/staticfiles:ro
      - media_volume:/app/media:ro
    depends_on:
      - web

volumes:
  mysql_data:
  static_volume:
  media_volume:
```

### 启动 Docker

```bash
# 构建镜像并启动容器
docker-compose up -d

# 查看日志
docker-compose logs -f web

# 进入容器
docker-compose exec web bash

# 停止容器
docker-compose down

# 清除所有数据
docker-compose down -v
```

---

## 生产环境部署

### 使用 Gunicorn + Nginx

#### 1. 安装 Gunicorn

```bash
pip install gunicorn
```

#### 2. 创建 Gunicorn 配置

`gunicorn_config.py`:

```python
import multiprocessing

bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 50
preload_app = True

accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
loglevel = "info"
```

#### 3. 创建 Systemd 服务

`/etc/systemd/system/system_demo.service`:

```ini
[Unit]
Description=Intelligent Resume Screening System
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/path/to/system_demo
Environment="PATH=/path/to/system_demo/venv/bin"
ExecStart=/path/to/system_demo/venv/bin/gunicorn \
    --config /path/to/system_demo/gunicorn_config.py \
    system_demo.wsgi:application

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable system_demo
sudo systemctl start system_demo
sudo systemctl status system_demo
```

#### 4. 配置 Nginx

`/etc/nginx/sites-available/system_demo`:

```nginx
upstream system_demo {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # 重定向到 HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL 证书配置（使用 Let's Encrypt）
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # SSL 安全配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    client_max_body_size 50M;

    access_log /var/log/nginx/system_demo_access.log;
    error_log /var/log/nginx/system_demo_error.log;

    location / {
        proxy_pass http://system_demo;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }

    # 静态文件
    location /static/ {
        alias /path/to/system_demo/staticfiles/;
        expires 30d;
    }

    # 媒体文件
    location /media/ {
        alias /path/to/system_demo/media/;
        expires 7d;
    }
}
```

启用网站：

```bash
sudo ln -s /etc/nginx/sites-available/system_demo /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 5. SSL 证书配置（Let's Encrypt）

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot certonly --nginx -d yourdomain.com -d www.yourdomain.com
sudo certbot renew --dry-run  # 测试自动续期
```

### 生产环境检查清单

```bash
# 1. 检查 Django 配置
python manage.py check --deploy

# 2. 收集静态文件
python manage.py collectstatic --noinput

# 3. 运行测试
python manage.py test

# 4. 检查数据库迁移
python manage.py showmigrations

# 5. 检查日志权限
mkdir -p /var/log/gunicorn
chmod 755 /var/log/gunicorn
```

### 监控与日志

```bash
# 查看 Gunicorn 日志
tail -f /var/log/gunicorn/error.log
tail -f /var/log/gunicorn/access.log

# 查看 Nginx 日志
tail -f /var/log/nginx/system_demo_access.log
tail -f /var/log/nginx/system_demo_error.log

# 查看系统日志
sudo journalctl -u system_demo -f
```

---

## 常见问题排查

### 问题 1：MySQL 连接失败

```
Error connecting to MySQL server
```

**解决方案：**
```bash
# 1. 检查 MySQL 是否运行
sudo systemctl status mysql

# 2. 检查连接信息
mysql -u root -p -h 127.0.0.1

# 3. 检查 .env 文件配置
grep DB_ .env

# 4. 测试 Django 连接
python manage.py dbshell
```

### 问题 2：DeepSeek API 超时

```
requests.exceptions.ConnectTimeout: DeepSeek API connection timeout
```

**解决方案：**
```bash
# 1. 检查网络连接
ping api.deepseek.com

# 2. 检查 API Key
grep DEEPSEEK_API_KEY .env

# 3. 检查配额限制
# 登录 DeepSeek 控制面板检查账户状态

# 4. 增加超时时间
# 编辑 .env：DEEPSEEK_API_TIMEOUT=120
```

### 问题 3：静态文件 404

```
Static file not found: /static/css/style.css
```

**解决方案：**
```bash
# 1. 收集静态文件
python manage.py collectstatic

# 2. 检查 DEBUG 设置
grep DEBUG .env

# 3. 检查 Nginx 配置
sudo nginx -t

# 4. 重新加载 Nginx
sudo systemctl reload nginx
```

### 问题 4：权限错误

```
PermissionError: [Errno 13] Permission denied
```

**解决方案：**
```bash
# 1. 修复媒体文件夹权限
chmod -R 755 media/

# 2. 修复日志文件夹权限
chmod -R 755 logs/

# 3. 修复数据库文件权限
sudo chown -R mysql:mysql /var/lib/mysql
```

---

## 备份与恢复

### 备份数据库

```bash
# 完整备份
mysqldump -u root -p system_demo_db > backup_$(date +%Y%m%d_%H%M%S).sql

# 压缩备份
mysqldump -u root -p system_demo_db | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz
```

### 恢复数据库

```bash
# 从备份恢复
mysql -u root -p system_demo_db < backup_20240101_120000.sql

# 从压缩备份恢复
gunzip < backup_20240101_120000.sql.gz | mysql -u root -p system_demo_db
```

### 备份媒体文件

```bash
tar -czf media_backup_$(date +%Y%m%d_%H%M%S).tar.gz media/
```

---

更多问题？请在 [GitHub Issues](../../issues) 中提问！
