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

# 最终阶段 - 用最小镜像保存构建结果
FROM alpine:latest

# 安装必要工具（可选）
RUN apk add --no-cache rsync

# 创建目录
RUN mkdir -p /app/dist

# 从构建阶段复制构建结果
COPY --from=build-stage /app/dist /tmp/dist

# 创建启动脚本来复制文件到共享卷
RUN echo '#!/bin/sh\n\
if [ -d "/tmp/dist" ] && [ "$(ls -A /tmp/dist)" ]; then\n\
  echo "Copying frontend build files..."\n\
  cp -r /tmp/dist/* /app/dist/\n\
  echo "Frontend files copied successfully"\n\
else\n\
  echo "No build files found"\n\
fi\n\
tail -f /dev/null' > /entrypoint.sh && chmod +x /entrypoint.sh

# 保持容器运行（作为数据容器）
CMD ["/entrypoint.sh"] 