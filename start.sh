#!/bin/bash
set -e

# 确保清理旧的数据（如果需要重新初始化）
if [ "$RESET_NEO4J" = "true" ]; then
    echo "Resetting Neo4j data..."
    rm -rf /var/lib/neo4j/data/databases/
    rm -rf /var/lib/neo4j/data/transactions/
    # 清除认证相关的缓存和锁定文件
    rm -rf /var/lib/neo4j/data/dbms/
    rm -f /var/lib/neo4j/data/.neo4j_initialized
fi

# 设置 Neo4j 初始密码
echo "Setting up Neo4j initial password..."
if [ ! -f /var/lib/neo4j/data/.neo4j_initialized ]; then
    echo "First time setup: setting initial password..."
    neo4j-admin dbms set-initial-password ${NEO4J_PASSWORD:-password}
    touch /var/lib/neo4j/data/.neo4j_initialized
else
    echo "Neo4j already initialized, skipping password setup"
    # 如果设置了强制重置标志，仍然尝试设置密码
    if [ "$RESET_NEO4J" = "true" ]; then
        echo "RESET_NEO4J is true, forcing password reset..."
        neo4j-admin dbms set-initial-password ${NEO4J_PASSWORD:-password} || true
        # 删除标记文件，以便下次能重新初始化
        rm -f /var/lib/neo4j/data/.neo4j_initialized
        touch /var/lib/neo4j/data/.neo4j_initialized
    fi
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
sleep 10

# 如果存在速率限制问题，等待更长时间
if [ "$RESET_NEO4J" = "true" ]; then
    echo "Reset mode: waiting extra time for Neo4j to fully initialize..."
    sleep 10
fi

# 测试Neo4j连接（可选，用于调试）
echo "Testing Neo4j connection..."
max_attempts=5
attempt=1
while [ $attempt -le $max_attempts ]; do
    if echo "RETURN 1;" | cypher-shell -u ${NEO4J_USER:-neo4j} -p ${NEO4J_PASSWORD:-password} 2>/dev/null; then
        echo "✅ Neo4j connection successful!"
        break
    else
        echo "⏳ Neo4j connection attempt $attempt/$max_attempts failed, waiting..."
        if [ $attempt -eq $max_attempts ]; then
            echo "❌ Failed to connect to Neo4j after $max_attempts attempts"
            echo "💡 Try setting RESET_NEO4J=true to reset the database"
        fi
        sleep 5
        ((attempt++))
    fi
done

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