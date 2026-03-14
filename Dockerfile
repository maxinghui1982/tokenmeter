# 多阶段构建 - 生产优化版
# 阶段1: 构建依赖
FROM python:3.11-slim as builder

WORKDIR /app

# 安装构建依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制并安装Python依赖
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir --user -r requirements.txt

# 阶段2: 生产镜像
FROM python:3.11-slim as production

# 创建非root用户（安全最佳实践）
RUN groupadd -r tokenmeter && useradd -r -g tokenmeter tokenmeter

WORKDIR /app

# 从builder阶段复制Python包
COPY --from=builder /root/.local /home/tokenmeter/.local
ENV PATH=/home/tokenmeter/.local/bin:$PATH

# 复制应用代码
COPY --chown=tokenmeter:tokenmeter src/ ./src/
COPY --chown=tokenmeter:tokenmeter config/ ./config/

# 创建数据目录并设置权限
RUN mkdir -p /app/data /app/logs && \
    chown -R tokenmeter:tokenmeter /app

# 切换到非root用户
USER tokenmeter

# 暴露端口
EXPOSE 8080

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/api/v1/health')" || exit 1

# 启动命令
CMD ["python", "-m", "src.main"]

# 阶段3: 开发镜像（包含测试依赖）
FROM production as development

USER root

# 安装开发依赖
COPY requirements-dev.txt ./
RUN pip install --no-cache-dir --user -r requirements-dev.txt

# 复制测试代码
COPY --chown=tokenmeter:tokenmeter tests/ ./tests/
COPY --chown=tokenmeter:tokenmeter pyproject.toml ./

USER tokenmeter

# 开发模式默认命令
CMD ["python", "-m", "pytest", "tests/", "-v"]
