# 🐳 Docker 全栈部署指南 - 前后端分离

## 📋 前置要求

确保您的系统已安装：
- Docker
- Docker Compose

## 🚀 快速启动

### 1. 启动所有服务
```bash
# 构建并启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f backend
```

### 2. 访问服务
- **前端应用**: http://localhost （Vue 3 + Vite SPA）
- **后端 API**: http://localhost/api/ （Django REST API）
- **API 文档**: http://localhost/swagger/ （Swagger UI）
- **MySQL**: localhost:3306
- **Redis**: localhost:6380

### 3. 测试应用
```bash
# 访问前端应用
open http://localhost

# 测试 API 接口
curl http://localhost/api/schools/

# 查看 API 文档
curl http://localhost/swagger/

# 获取学校统计
curl http://localhost/api/schools/stats/
```

## 🛠️ 服务架构

本项目采用**前后端分离**架构，使用 **Nginx** 作为反向代理：

```
用户请求 → Nginx (80) → Frontend (Vue SPA) / Backend API (Django)
                    ↓
              MySQL (3306) + Redis (6380)
```

### Nginx 反向代理
- **镜像**: nginx:alpine
- **端口**: 80 (对外访问)
- **功能**: 
  - `/` → 前端 Vue 应用
  - `/api/` → 后端 Django API
  - `/swagger/` → API 文档
- **配置**: `nginx/nginx.conf`

### Frontend 应用 (Vue 3)
- **技术栈**: Vue 3 + Vite + TypeScript
- **构建**: 多阶段 Docker 构建 (`frontend/Dockerfile`)
- **功能**: SPA 单页应用，路由支持
- **部署**: Nginx 静态文件服务

### Backend 应用 (Django)
- **技术栈**: Django + Django REST Framework
- **构建**: 基于 `backend/Dockerfile`
- **端口**: 8080 (内部)
- **环境**: 开发环境 (DEV)
- **配置**: 使用 `settings.docker.json`

### MySQL 数据库
- **镜像**: mysql:8.0
- **端口**: 3306
- **数据库**: dev_yundisoft
- **用户**: root
- **密码**: fgdTv@4629uGdY
- **数据持久化**: Docker volume `mysql_data`

### Redis 缓存
- **镜像**: redis:7-alpine
- **端口**: 6380
- **密码**: HaWSD*9265tZYj
- **数据持久化**: Docker volume `redis_data`

## 🔧 常用命令

### 启动和停止
```bash
# 启动所有服务
docker-compose up -d

# 停止所有服务
docker-compose down

# 停止并删除数据卷（谨慎使用）
docker-compose down -v
```

### 查看状态和日志
```bash
# 查看服务状态
docker-compose ps

# 查看所有日志
docker-compose logs

# 查看特定服务日志
docker-compose logs frontend
docker-compose logs backend
docker-compose logs nginx
docker-compose logs mysql
docker-compose logs redis

# 实时查看日志
docker-compose logs -f nginx
docker-compose logs -f backend
```

### 重新构建
```bash
# 重新构建 backend 服务
docker-compose build backend

# 重新构建并启动
docker-compose up -d --build backend
```

### 进入容器
```bash
# 进入 nginx 容器
docker-compose exec nginx sh

# 进入 frontend 容器
docker-compose exec frontend sh

# 进入 backend 容器
docker-compose exec backend bash

# 进入 MySQL 容器
docker-compose exec mysql mysql -u root -p

# 进入 Redis 容器
docker-compose exec redis redis-cli -p 6380 -a HaWSD*9265tZYj
```

## 🔍 故障排除

### 1. 数据库连接失败
```bash
# 检查 MySQL 是否正常启动
docker-compose logs mysql

# 手动测试数据库连接
docker-compose exec mysql mysql -u root -p -e "SHOW DATABASES;"
```

### 2. Backend 启动失败
```bash
# 查看 backend 日志
docker-compose logs backend

# 重新构建 backend
docker-compose build backend --no-cache
```

### 3. Redis 连接问题
```bash
# 检查 Redis 状态
docker-compose exec redis redis-cli -p 6380 -a HaWSD*9265tZYj ping
```

### 4. 端口冲突
如果端口被占用，请修改 `docker-compose.yml` 中的端口映射：
```yaml
ports:
  - "8081:8080"  # 将本地端口改为 8081
```

## 📊 数据管理

### 数据库初始化
首次启动时，Django 会自动运行数据库迁移：
```bash
python manage.py makemigrations
python manage.py migrate
```

### 数据备份
```bash
# 备份 MySQL 数据
docker-compose exec mysql mysqldump -u root -p dev_yundisoft > backup.sql

# 恢复数据
docker-compose exec -T mysql mysql -u root -p dev_yundisoft < backup.sql
```

## 🔐 安全说明

**⚠️ 注意**: 当前配置使用的是开发环境密码，生产环境请务必：
1. 修改所有默认密码
2. 使用环境变量管理敏感信息
3. 启用 HTTPS
4. 配置防火墙规则

## 📈 扩展配置

### 生产环境部署
1. 修改 `docker-compose.yml` 中的密码
2. 创建生产环境配置文件
3. 使用 Docker Secrets 管理敏感信息
4. 配置反向代理 (Nginx)
5. 设置日志管理和监控

### 性能优化
1. 调整 MySQL 配置参数
2. 配置 Redis 内存限制
3. 使用 Gunicorn 替代开发服务器
4. 启用静态文件缓存 