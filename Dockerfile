# 基于官方 Python 3.9 镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装系统级依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    wget \
    unzip \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安装其他 Python 依赖
RUN pip install --upgrade pip && \
    pip install \
    --index-url https://mirrors.cloud.tencent.com/pypi/simple \
    transformers \
    openai \
    pymilvus \
    beautifulsoup4 \
    pdfplumber \
    faiss-cpu \
    # Torch + CUDA 11.7 wheels (adapt if PyTorch version changes):
    torch==1.13.1+cu117 \
    torchvision==0.14.1+cu117 \
    torchaudio==0.13.1 \
    --extra-index-url https://download.pytorch.org/whl/cu117 \
    sentence-transformers \
    numpy \
    pandas \
    lxml \
    sgmllib3k \
    langchain \
    # If you are using Jupyter inside Docker (not mandatory):
    jupyter \
    # For script argument parsing, debugging, etc.:
    click \
    # (Add any other project dependencies here)
    && rm -rf /root/.cache/pip

# 安装 Milvus（如果需要本地安装的 Milvus 服务）
# RUN pip install milvus

# 创建并进入应用目录
COPY . /app

# 可选：如果需要安装与 Milvus 相关的其他系统依赖，取消以下注释：
# RUN apt-get update && apt-get install -y \
#     libboost-all-dev \
#     && rm -rf /var/lib/apt/lists/*

# 设置容器启动时的命令
# CMD ["python", "app.py"]
