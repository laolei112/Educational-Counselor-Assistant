# 构建阶段 - 只用于构建前端静态文件
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

# 最终阶段 - 直接将构建结果放到正确位置
FROM alpine:latest

# 创建目录
RUN mkdir -p /app/dist

# 直接从构建阶段复制构建结果到最终位置
COPY --from=build-stage /app/dist /app/dist

# 创建简单的启动脚本
RUN echo '#!/bin/sh' > /entrypoint.sh && \
    echo 'echo "Frontend container starting..."' >> /entrypoint.sh && \
    echo 'echo "Files in /app/dist:"' >> /entrypoint.sh && \
    echo 'ls -la /app/dist/' >> /entrypoint.sh && \
    echo 'echo "Frontend container ready, keeping alive..."' >> /entrypoint.sh && \
    echo 'tail -f /dev/null' >> /entrypoint.sh && \
    chmod +x /entrypoint.sh

# 保持容器运行
CMD ["/entrypoint.sh"] 