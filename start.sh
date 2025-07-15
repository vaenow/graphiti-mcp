#!/bin/bash
set -e

# 确保清理旧的数据（如果需要重新初始化）
if [ "$RESET_NEO4J" = "true" ]; then
    echo "Resetting Neo4j data..."
    rm -rf /var/lib/neo4j/data/databases/
    rm -rf /var/lib/neo4j/data/transactions/
fi

# 设置 Neo4j 初始密码
echo "Setting up Neo4j initial password..."
if [ ! -f /var/lib/neo4j/data/.neo4j_initialized ]; then
    echo "First time setup: setting initial password..."
    neo4j-admin dbms set-initial-password ${NEO4J_PASSWORD:-password}
    touch /var/lib/neo4j/data/.neo4j_initialized
else
    echo "Neo4j already initialized, using existing password"
    # 简单策略：如果已经初始化，就信任现有的密码设置
    # 如果真的需要重置，使用 RESET_NEO4J=true
fi

# 启动 Neo4j
echo "Starting Neo4j..."
neo4j start

# 等待 Neo4j 启动
echo "Waiting for Neo4j to start..."
for i in {1..30}; do
    if neo4j status > /dev/null 2>&1; then
        echo "Neo4j started successfully"
        break
    fi
    echo "Neo4j is starting... ($i/30)"
    sleep 2
done

# 验证 Neo4j 是否真的启动了
if ! neo4j status > /dev/null 2>&1; then
    echo "Failed to start Neo4j after 60 seconds"
    exit 1
fi

# 额外等待确保 Neo4j 完全就绪
echo "Waiting for Neo4j to be fully ready..."
sleep 5

# 运行应用
echo "Starting Graphiti MCP Server..."
if [ -f "mcp_server.py" ]; then
    python mcp_server.py
elif [ -f "main.py" ]; then
    python main.py
elif [ -f "app.py" ]; then
    python app.py
else
    echo "No application file found. Starting Python shell..."
    python
fi 