FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements文件并安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 设置环境变量
ENV PYTHONPATH=/app
ENV DJANGO_SETTINGS_MODULE=backend.settings
ENV GPT_ENV=DEV

# 暴露端口
EXPOSE 8080

# 创建启动脚本
RUN echo '#!/bin/bash\n\
echo "Waiting for database..."\n\
while ! nc -z mysql 3306; do\n\
  sleep 0.1\n\
done\n\
echo "Database connected!"\n\
\n\
echo "Running migrations..."\n\
python manage.py makemigrations\n\
python manage.py migrate\n\
\n\
echo "Starting Django server..."\n\
python manage.py runserver 0.0.0.0:8080' > start.sh

RUN chmod +x start.sh

# 安装netcat用于检查数据库连接
RUN apt-get update && apt-get install -y netcat-traditional && rm -rf /var/lib/apt/lists/*

CMD ["./start.sh"] 