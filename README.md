# Graphiti Docker 部署指南

基于 [Graphiti](https://github.com/getzep/graphiti) 知识图谱的 Docker 部署方案，包含 Neo4j 数据库和 Graphiti 应用的完整容器化解决方案。

## 📋 前置要求

- Docker
- OpenAI API Key

## 🚀 快速开始

### 1. 设置环境变量
```bash
cp env.example .env
# 编辑 .env 文件，添加你的 OpenAI API Key
```

### 2. 构建镜像
```bash
docker build -t graphiti-app .
```

### 3. 运行容器
```bash
docker run -d \
  --name graphiti-app \
  -p 7474:7474 \
  -p 7687:7687 \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your_openai_api_key_here \
  graphiti-app
```

### 4. 访问服务
- Neo4j Browser: http://localhost:7474 (用户名: neo4j, 密码: password)
- 应用日志: `docker logs -f graphiti-app`

## ⚙️ 配置

### 环境变量

| 变量名 | 描述 | 默认值 |
|--------|------|--------|
| `OPENAI_API_KEY` | OpenAI API 密钥 | 必填 |
| `NEO4J_URI` | Neo4j 连接 URI | `bolt://localhost:7687` |
| `NEO4J_USER` | Neo4j 用户名 | `neo4j` |
| `NEO4J_PASSWORD` | Neo4j 密码 | `password` |
| `USE_PARALLEL_RUNTIME` | 启用 Neo4j 并行运行时 | `false` |
| `GRAPHITI_TELEMETRY_ENABLED` | 启用遥测 | `true` |

### 端口

- **7474**: Neo4j HTTP 接口
- **7687**: Neo4j Bolt 协议
- **8000**: Graphiti 应用端口

## 🔧 运行选项

### 基础运行
```bash
docker run -d \
  --name graphiti-app \
  -p 7474:7474 \
  -p 7687:7687 \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your_openai_api_key_here \
  graphiti-app
```

### 开发模式（挂载代码目录）
```bash
docker run -d \
  --name graphiti-app \
  -p 7474:7474 \
  -p 7687:7687 \
  -p 8000:8000 \
  -v $(pwd):/app \
  -e OPENAI_API_KEY=your_openai_api_key_here \
  graphiti-app
```

### 数据持久化
```bash
docker run -d \
  --name graphiti-app \
  -p 7474:7474 \
  -p 7687:7687 \
  -p 8000:8000 \
  -v graphiti_data:/var/lib/neo4j/data \
  -v graphiti_logs:/var/lib/neo4j/logs \
  -e OPENAI_API_KEY=your_openai_api_key_here \
  graphiti-app
```

## 📊 监控和日志

### 查看日志
```bash
# 应用日志
docker logs -f graphiti-app

# 进入容器查看详细日志
docker exec -it graphiti-app bash
```

### 健康检查
```bash
# 检查 Neo4j 状态
curl http://localhost:7474/

# 检查容器状态
docker ps
```

## ��️ 自定义配置

### Neo4j 配置

如果需要自定义 Neo4j 配置：

1. 创建 `neo4j.conf` 文件
2. 运行时挂载配置文件：
   ```bash
   docker run -d \
     --name graphiti-app \
     -p 7474:7474 \
     -p 7687:7687 \
     -p 8000:8000 \
     -v $(pwd)/neo4j.conf:/etc/neo4j/neo4j.conf \
     -e OPENAI_API_KEY=your_openai_api_key_here \
     graphiti-app
   ```

### 应用代码

- `main.py`: 主应用文件，包含 Graphiti 示例代码
- 可以根据需要修改此文件来实现你的业务逻辑

## 📈 性能优化

### 内存设置

通过环境变量调整 Neo4j 内存使用：

```bash
docker run -d \
  --name graphiti-app \
  -p 7474:7474 \
  -p 7687:7687 \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your_openai_api_key_here \
  -e NEO4J_dbms_memory_pagecache_size=2G \
  -e NEO4J_dbms_memory_heap_initial__size=2G \
  -e NEO4J_dbms_memory_heap_max__size=2G \
  graphiti-app
```

## 🔍 故障排除

### 常见问题

1. **容器启动失败**
   ```bash
   # 查看详细错误信息
   docker logs graphiti-app
   ```

2. **无法连接到 Neo4j**
   ```bash
   # 检查 Neo4j 服务状态
   docker exec -it graphiti-app neo4j status
   ```

3. **OpenAI API 错误**
   - 确认 API Key 设置正确
   - 检查网络连接

### 清理和重启

```bash
# 停止并删除容器
docker stop graphiti-app
docker rm graphiti-app

# 删除镜像（如需重新构建）
docker rmi graphiti-app

# 重新构建并运行
docker build -t graphiti-app .
docker run -d \
  --name graphiti-app \
  -p 7474:7474 \
  -p 7687:7687 \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your_openai_api_key_here \
  graphiti-app
```

### 数据备份

```bash
# 备份 Neo4j 数据
docker exec graphiti-app neo4j-admin dump --database=neo4j --to=/var/lib/neo4j/data/backup.dump

# 从容器复制备份文件
docker cp graphiti-app:/var/lib/neo4j/data/backup.dump ./backup.dump
```

## 📚 相关资源

- [Graphiti GitHub](https://github.com/getzep/graphiti)
- [Graphiti 文档](https://help.getzep.com/graphiti)
- [Neo4j 文档](https://neo4j.com/docs/)
- [Docker 文档](https://docs.docker.com/)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进这个部署配置！