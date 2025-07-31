# 使用 Mambaforge 作为基础镜像，包含 conda/mamba
FROM mambaforge/mambaforge:latest

# 设置工作目录
WORKDIR /app

# 安装 Pixi
RUN curl -fsSL https://pixi.sh/install.sh | bash && \
    echo 'export PATH="$HOME/.pixi/bin:$PATH"' >> ~/.bashrc

# 复制项目文件
COPY . /app

# 使用 Pixi 安装所有依赖
RUN eval "$(~/.pixi/bin/pixi shell-hook)" && \
    ~/.pixi/bin/pixi install

# 设置容器启动时的命令
# 激活 Pixi 环境并运行应用
CMD ["bash", "-c", "eval \"$(~/.pixi/bin/pixi shell-hook)\" && python run_job.py"]
