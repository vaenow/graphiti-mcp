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

# 创建启动脚本
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
# 确保清理旧的数据（如果需要重新初始化）\n\
if [ "$RESET_NEO4J" = "true" ]; then\n\
    echo "Resetting Neo4j data..."\n\
    rm -rf /var/lib/neo4j/data/databases/\n\
    rm -rf /var/lib/neo4j/data/transactions/\n\
fi\n\
\n\
# 设置 Neo4j 初始密码\n\
echo "Setting up Neo4j initial password..."\n\
if [ ! -f /var/lib/neo4j/data/.neo4j_initialized ]; then\n\
    neo4j-admin dbms set-initial-password ${NEO4J_PASSWORD:-password}\n\
    touch /var/lib/neo4j/data/.neo4j_initialized\n\
else\n\
    echo "Neo4j already initialized, skipping password setup"\n\
fi\n\
\n\
# 启动 Neo4j\n\
echo "Starting Neo4j..."\n\
neo4j start\n\
\n\
# 等待 Neo4j 启动\n\
echo "Waiting for Neo4j to start..."\n\
for i in {1..30}; do\n\
    if neo4j status > /dev/null 2>&1; then\n\
        echo "Neo4j started successfully"\n\
        break\n\
    fi\n\
    echo "Neo4j is starting... ($i/30)"\n\
    sleep 2\n\
done\n\
\n\
# 验证 Neo4j 是否真的启动了\n\
if ! neo4j status > /dev/null 2>&1; then\n\
    echo "Failed to start Neo4j after 60 seconds"\n\
    exit 1\n\
fi\n\
\n\
# 额外等待确保 Neo4j 完全就绪\n\
echo "Waiting for Neo4j to be fully ready..."\n\
sleep 5\n\
\n\
# 运行应用\n\
echo "Starting Graphiti MCP Server..."\n\
if [ -f "mcp_server.py" ]; then\n\
    python mcp_server.py\n\
elif [ -f "main.py" ]; then\n\
    python main.py\n\
elif [ -f "app.py" ]; then\n\
    python app.py\n\
else\n\
    echo "No application file found. Starting Python shell..."\n\
    python\n\
fi\n\
' > /app/start.sh && chmod +x /app/start.sh

# 暴露端口
EXPOSE 7474 7687 8000

# 设置健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD neo4j status && curl -f http://localhost:7474/ || exit 1

# 启动命令
CMD ["/app/start.sh"] 