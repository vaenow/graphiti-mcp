# Graphiti MCP Server 使用指南

本文档介绍如何使用 Graphiti MCP 服务器与各种 AI 客户端进行交互。

## 📋 目录

- [快速开始](#快速开始)
- [客户端配置](#客户端配置)
- [MCP 工具使用](#mcp-工具使用)
- [示例操作](#示例操作)
- [故障排除](#故障排除)

## 🚀 快速开始

### 1. 启动服务

```bash
# 使用 Docker Compose
docker-compose up -d

# 或直接运行启动脚本 (推荐)
chmod +x start.sh
./start.sh

# 或仅运行 MCP 服务器 (需要 Neo4j 已启动)
python mcp_server.py
```

### 启动脚本说明

`start.sh` 脚本会自动完成以下操作：

1. **Neo4j 初始化和启动**
   - 设置初始密码
   - 启动 Neo4j 服务
   - 等待服务就绪

2. **MCP 服务器启动**  
   - 启动 Graphiti MCP 服务器
   - 等待客户端连接

**环境变量配置:**
```bash
# 重置 Neo4j 数据和密码 (开发环境)
export RESET_NEO4J=true

# 自定义 Neo4j 密码（首次启动时生效）
export NEO4J_PASSWORD=your_password

# 启动脚本
./start.sh
```

### 常见问题解决

#### 认证失败问题
如果遇到 `The client is unauthorized due to authentication failure` 错误：

```bash
# 推荐方案：重置 Neo4j 数据（会清空所有数据）
export RESET_NEO4J=true
./start.sh

# Docker 环境中
docker run -e RESET_NEO4J=true ghcr.io/vaenow/graphiti-mcp:latest

# Kubernetes 环境中
kubectl set env statefulset/graphiti-mcp RESET_NEO4J=true -n vin
kubectl rollout restart statefulset/graphiti-mcp -n vin
```

> **⚠️ 注意**: `RESET_NEO4J=true` 会删除所有现有数据，仅在开发环境或确定要清空数据时使用。

### 2. 验证服务状态

```bash
# 检查 Neo4j 状态
curl http://localhost:7474/

# 检查容器日志
docker logs -f graphiti-mcp-server
```

## 🔧 客户端配置

### Claude Desktop

在 `claude_desktop_config.json` 中添加：

```json
{
  "mcpServers": {
    "graphiti": {
      "command": "python",
      "args": ["/path/to/graphiti-mcp/mcp_server.py"],
      "env": {
        "OPENAI_API_KEY": "your_openai_api_key_here",
        "NEO4J_URI": "bolt://localhost:7687",
        "NEO4J_USER": "neo4j",
        "NEO4J_PASSWORD": "password"
      }
    }
  }
}
```

### Cursor IDE

1. 打开 Cursor 设置
2. 导航到 Features > MCP
3. 点击 "+ Add New MCP Server"
4. 配置如下：
   - **Name**: Graphiti Knowledge Graph
   - **Type**: stdio
   - **Command**: `python /path/to/graphiti-mcp/mcp_server.py`

### LangGraph/LangChain

```python
from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters
from langchain_mcp_adapters.tools import load_mcp_tools

# 配置服务器参数
server_params = StdioServerParameters(
    command="python",
    args=["mcp_server.py"]
)

# 连接并使用工具
async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        tools = await load_mcp_tools(session)
        # 现在可以在 LangGraph agent 中使用这些工具
```

## 🛠️ MCP 工具使用

### 1. 添加片段 (add_episode)

向知识图谱添加新的信息片段。

**参数：**
- `name` (必需): 片段名称
- `content` (必需): 片段内容
- `episode_type` (可选): "text" 或 "json"，默认为 "text"
- `source_description` (可选): 来源描述

**示例：**
```json
{
  "name": "公司会议记录",
  "content": "今天的团队会议讨论了新产品的发布计划，预计在下个月推出。",
  "episode_type": "text",
  "source_description": "团队会议记录"
}
```

### 2. 搜索图谱 (search_graph)

在知识图谱中搜索相关信息。

**参数：**
- `query` (必需): 搜索查询
- `limit` (可选): 结果数量限制，默认为 5

**示例：**
```json
{
  "query": "产品发布计划",
  "limit": 10
}
```

### 3. 获取实体 (get_entities)

获取知识图谱中的实体信息。

**参数：**
- `entity_name` (可选): 特定实体名称
- `limit` (可选): 结果数量限制，默认为 10

**示例：**
```json
{
  "entity_name": "产品",
  "limit": 5
}
```

### 4. 获取社区 (get_communities)

获取知识图谱中的社区信息。

**参数：**
- `limit` (可选): 结果数量限制，默认为 10

**示例：**
```json
{
  "limit": 5
}
```

## 📚 资源访问

### 图谱架构信息

**URI**: `graphiti://graph/schema`

返回当前知识图谱的架构信息，包括节点类型、关系类型和属性定义。

### 图谱统计信息

**URI**: `graphiti://graph/stats`

返回知识图谱的统计信息，如节点数量、关系数量等。

## 💡 示例操作

### 完整工作流示例

1. **添加会议记录**
```bash
# 通过 MCP 客户端调用
add_episode(
    name="产品规划会议",
    content="讨论了 Q1 产品路线图，包括新功能开发和用户反馈整合。",
    episode_type="text"
)
```

2. **搜索相关信息**
```bash
# 搜索产品相关信息
search_graph(
    query="产品路线图",
    limit=5
)
```

3. **查看实体关系**
```bash
# 获取产品相关实体
get_entities(
    entity_name="产品",
    limit=10
)
```

### Claude Desktop 使用示例

在 Claude Desktop 中，你可以直接询问：

```
"请帮我在知识图谱中添加一条关于今天项目进展的记录：我们完成了数据库优化，性能提升了30%。"
```

Claude 会自动调用 `add_episode` 工具来执行此操作。

## 🔍 故障排除

### 常见问题

1. **连接失败**
   - 检查 Neo4j 是否正在运行
   - 验证环境变量配置
   - 确认端口未被占用

2. **认证错误**
   - 检查 OpenAI API 密钥
   - 验证 Neo4j 用户名和密码
   - 确认环境变量正确加载

3. **工具调用失败**
   - 查看 MCP 服务器日志
   - 验证输入参数格式
   - 检查 Graphiti 连接状态

### 调试命令

```bash
# 查看容器日志
docker logs -f graphiti-mcp-server

# 测试 Neo4j 连接
curl -u neo4j:password http://localhost:7474/db/data/

# 检查 MCP 服务器状态
python -c "import asyncio; from mcp_server import main; asyncio.run(main())"
```

### 日志分析

关键日志消息：
- `✅ Graphiti 初始化成功` - 服务器启动成功
- `🚀 Graphiti MCP 服务器已启动` - MCP 协议监听中
- `工具调用错误` - 工具执行问题

## 📞 支持和反馈

如果遇到问题或有改进建议，请：

1. 查看日志文件获取详细错误信息
2. 检查 [官方文档](https://help.getzep.com/graphiti)
3. 在 GitHub 仓库提交 Issue

---

## 📖 更多资源

- [Graphiti 官方文档](https://help.getzep.com/graphiti)
- [MCP 协议规范](https://modelcontextprotocol.io/docs)
- [Claude Desktop MCP 配置](https://docs.anthropic.com/en/docs/build-with-claude/mcp)
- [Cursor MCP 集成](https://cursor.directory/mcp) 