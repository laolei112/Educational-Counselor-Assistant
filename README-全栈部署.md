# 🌟 香港升学助手 - 全栈 Docker 部署指南

## 🏗️ 项目架构

本项目采用现代化的**前后端分离**架构，使用 Docker Compose 进行容器化部署：

```
┌─────────────────────────────────────────────────────┐
│                   用户访问                            │
│                http://localhost                     │
└─────────────────┬───────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────┐
│             Nginx 反向代理 (80)                      │
│  ┌─────────────┬─────────────┬─────────────────────┐ │
│  │      /      │   /api/     │     /swagger/       │ │
│  │   前端路由   │  后端 API   │    API 文档         │ │
└──┼─────────────┼─────────────┼─────────────────────┼─┘
   │             │             │                     │
┌──▼──────────┐ ┌▼─────────────▼─────────────────────▼─┐
│  Frontend   │ │             Backend                 │
│  Vue 3 SPA  │ │        Django + DRF                │
│  (静态文件)  │ │         (8080)                     │
└─────────────┘ └─┬─────────────────────────────────┬─┘
                  │                                 │
              ┌───▼─────┐                    ┌─────▼───┐
              │  MySQL  │                    │  Redis  │
              │ (3306)  │                    │ (6380)  │
              └─────────┘                    └─────────┘
```

## 🛠️ 技术栈

### 前端 (Frontend)
- **框架**: Vue 3 + Composition API
- **构建工具**: Vite
- **语言**: TypeScript
- **状态管理**: Pinia
- **路由**: Vue Router 4
- **部署**: Nginx 静态文件服务

### 后端 (Backend)
- **框架**: Django + Django REST Framework
- **语言**: Python 3.9
- **数据库**: MySQL 8.0
- **缓存**: Redis 7
- **API 文档**: Swagger (drf_yasg)
- **跨域**: django-cors-headers

### 基础设施 (Infrastructure)
- **反向代理**: Nginx
- **容器化**: Docker + Docker Compose
- **数据持久化**: Docker Volumes

## 🚀 快速开始

### 1. 前置要求
```bash
# 检查 Docker 版本
docker --version
docker-compose --version

# 最低要求
# Docker: 20.0+
# Docker Compose: 1.29+
```

### 2. 一键启动

**Windows 用户**：
```cmd
start-full-stack.bat
```

**Linux/Mac 用户**：
```bash
chmod +x start-docker.sh
./start-docker.sh
```

**手动启动**：
```bash
# 构建并启动所有服务
docker-compose up -d --build

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 3. 验证部署

等待 15-30 秒服务完全启动后：

```bash
# 检查前端
curl http://localhost

# 检查后端 API
curl http://localhost/api/schools/

# 检查服务状态
docker-compose ps
```

## 🌐 访问地址

| 服务 | 地址 | 说明 |
|------|------|------|
| **前端应用** | http://localhost | Vue 3 单页应用 |
| **后端 API** | http://localhost/api/ | Django REST API |
| **API 文档** | http://localhost/swagger/ | Swagger UI 接口文档 |
| **Nginx 健康检查** | http://localhost/nginx-health | 反向代理状态 |
| **MySQL** | localhost:3306 | 数据库连接 |
| **Redis** | localhost:6380 | 缓存连接 |

## 📋 容器服务

| 容器名 | 镜像 | 端口映射 | 职责 |
|--------|------|----------|------|
| `edu_nginx` | nginx:alpine | 80:80 | 反向代理、静态文件服务 |
| `edu_frontend` | 自构建 | - | Vue 3 前端应用 |
| `edu_backend` | 自构建 | - | Django 后端 API |
| `edu_mysql` | mysql:8.0 | 3306:3306 | 数据库 |
| `edu_redis` | redis:7-alpine | 6380:6380 | 缓存 |

## 🔧 开发调试

### 查看日志
```bash
# 查看所有服务日志
docker-compose logs

# 查看特定服务实时日志
docker-compose logs -f frontend
docker-compose logs -f backend
docker-compose logs -f nginx

# 查看最近 50 行日志
docker-compose logs --tail=50 backend
```

### 进入容器调试
```bash
# 进入前端容器
docker-compose exec frontend sh

# 进入后端容器
docker-compose exec backend bash

# 进入数据库
docker-compose exec mysql mysql -u root -p

# 进入 Redis
docker-compose exec redis redis-cli -p 6380 -a HaWSD*9265tZYj
```

### 重新构建服务
```bash
# 重新构建单个服务
docker-compose build frontend
docker-compose build backend

# 重新构建并启动
docker-compose up -d --build frontend
```

## 🧪 测试验证

### API 接口测试
```bash
# 获取学校列表
curl "http://localhost/api/schools/"

# 获取学校详情
curl "http://localhost/api/schools/1/"

# 获取统计信息
curl "http://localhost/api/schools/stats/"

# 按类型筛选
curl "http://localhost/api/schools/?type=secondary"
```

### 前端功能测试
```bash
# 访问主页
open http://localhost

# 检查前端路由
open http://localhost/schools
open http://localhost/about
```

## 🛑 停止和清理

```bash
# 停止所有服务
docker-compose down

# 停止并删除数据卷（⚠️ 会丢失数据）
docker-compose down -v

# 清理 Docker 缓存
docker system prune -f
```

## 🔍 故障排除

### 1. 端口冲突
```bash
# 检查端口占用
netstat -tulpn | grep :80
netstat -tulpn | grep :3306

# 修改端口映射
# 编辑 docker-compose.yml 中的 ports 配置
```

### 2. 容器启动失败
```bash
# 查看详细错误
docker-compose logs [service_name]

# 检查容器状态
docker-compose ps

# 重新构建问题容器
docker-compose build --no-cache [service_name]
```

### 3. 数据库连接问题
```bash
# 检查 MySQL 是否就绪
docker-compose exec mysql mysql -u root -p -e "SELECT 1;"

# 检查 Django 数据库配置
docker-compose exec backend python manage.py check --database default
```

### 4. 前端构建失败
```bash
# 查看前端构建日志
docker-compose logs frontend

# 手动构建测试
cd frontend
npm install
npm run build
```

## 📈 性能优化

### 生产环境建议
1. **启用 HTTPS**
2. **配置 CDN**
3. **优化 Nginx 缓存**
4. **启用 gzip 压缩**
5. **设置合适的安全头**

### 扩展配置
```bash
# 水平扩展后端
docker-compose up -d --scale backend=3

# 使用外部数据库
# 修改 docker-compose.yml 中的数据库配置
```

## 🔐 安全考虑

⚠️ **当前配置仅适用于开发环境**

生产环境请务必：
- 修改所有默认密码
- 启用 HTTPS
- 配置防火墙
- 使用环境变量管理敏感信息
- 定期更新 Docker 镜像

## 📞 支持

如果遇到问题：
1. 查看本文档的故障排除部分
2. 检查 Docker 和 Docker Compose 版本
3. 查看容器日志获取详细错误信息
4. 确保系统资源充足（内存 > 2GB） 