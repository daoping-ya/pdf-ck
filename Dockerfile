# 使用官方 Python 轻量级镜像
FROM python:3.10-slim

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PDF_PROCESSOR_PORT=5000 \
    PDF_PROCESSOR_HOST=0.0.0.0

# 安装系统依赖
# poppler-utils: 用于 pdf2image
# libmagic1: 用于文件类型检测
# libgl1, libglib2.0-0: 用于 opencv (pdf2docx, rapidocr)
RUN apt-get update && apt-get install -y \
    poppler-utils \
    libmagic1 \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY backend/requirements.txt backend/requirements.txt

# 安装 Python 依赖
# 注意: 额外安装 python-magic 因为 requirements.txt 中的 python-magic-bin 是 Windows 专用的
RUN pip install --no-cache-dir -r backend/requirements.txt && \
    pip install --no-cache-dir python-magic

# 复制项目文件
COPY backend/ backend/
COPY frontend/ frontend/

# 创建必要的目录
RUN mkdir -p backend/uploads/temp backend/uploads/processed backend/data

# 暴露端口
EXPOSE 5000

# 切换到后端目录启动应用
WORKDIR /app/backend

# 启动命令
CMD ["python", "app.py"]
