# 构建阶段
FROM node:18-alpine as build-stage

# 设置工作目录
WORKDIR /app

# 复制 package.json 和 package-lock.json
COPY package*.json ./

# 安装依赖（构建时需要开发依赖）
RUN npm ci

# 复制源代码
COPY . .

# 构建应用（跳过类型检查以避免 Docker 构建问题）
RUN npm run build:docker

# 生产阶段 - 使用 nginx 提供静态文件服务
FROM nginx:alpine as production-stage

# 删除默认的 nginx 静态资源
RUN rm -rf /usr/share/nginx/html/*

# 从构建阶段复制构建结果到 nginx 目录
COPY --from=build-stage /app/dist /usr/share/nginx/html

# 复制自定义的 nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

# 启动 nginx
CMD ["nginx", "-g", "daemon off;"] 