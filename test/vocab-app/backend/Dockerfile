FROM python:3.9-slim

WORKDIR /app

# 首先只复制依赖文件，这样可以利用缓存
COPY requirements.txt .

# 安装系统依赖和Python依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir -r requirements.txt

# 创建必要的目录
RUN mkdir -p /app/logs

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    FLASK_APP=app.py \
    FLASK_ENV=production

# 最后才复制应用代码，这样代码改动不会触发依赖重新安装
COPY . .

# 添加健康检查
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:5000/health || exit 1

# 暴露端口
EXPOSE 5000

# 使用 gunicorn 启动应用
CMD ["gunicorn", "--worker-class", "eventlet", "--workers", "1", "--bind", "0.0.0.0:5000", "app:app"] 