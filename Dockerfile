# 使用 Python 3.11 作为基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV NEO4J_PASSWORD=password

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg \
    software-properties-common \
    default-jre \
    && rm -rf /var/lib/apt/lists/*

# 安装 Neo4j
RUN wget -O - https://debian.neo4j.com/neotechnology.gpg.key | gpg --dearmor -o /etc/apt/keyrings/neotechnology.gpg \
    && echo 'deb [signed-by=/etc/apt/keyrings/neotechnology.gpg] https://debian.neo4j.com stable 5' > /etc/apt/sources.list.d/neo4j.list \
    && apt-get update \
    && apt-get install -y neo4j=1:5.26.0 \
    && rm -rf /var/lib/apt/lists/*

# 创建 Neo4j 数据目录并设置权限
RUN mkdir -p /var/lib/neo4j/data /var/lib/neo4j/logs /var/lib/neo4j/import /var/lib/neo4j/plugins \
    && chown -R neo4j:neo4j /var/lib/neo4j

# Neo4j 配置可以通过环境变量或挂载卷来自定义
# 如需自定义配置，运行时使用: -v $(pwd)/neo4j.conf:/etc/neo4j/neo4j.conf

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 设置启动脚本权限
RUN chmod +x /app/start.sh

# 暴露端口
EXPOSE 7474 7687 8000

# 设置健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD neo4j status && curl -f http://localhost:7474/ || exit 1

# 启动命令
CMD ["./start.sh"] 