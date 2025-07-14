# Graphiti Docker 部署指南

基于 [Graphiti](https://github.com/getzep/graphiti) 知识图谱的 Docker 部署方案，包含 Neo4j 数据库和 Graphiti 应用的完整容器化解决方案。

**中文** | [English](README.md)

[![Docker Build](https://github.com/vaenow/graphiti-mcp/actions/workflows/docker-build.yml/badge.svg)](https://github.com/vaenow/graphiti-mcp/actions/workflows/docker-build.yml)
[![Docker Image](https://img.shields.io/badge/docker-ghcr.io-blue.svg)](https://ghcr.io/vaenow/graphiti-mcp)

## 📋 前置要求

- Docker
- OpenAI API Key

## 🚀 快速开始

### 方案一：使用预构建镜像（推荐）

最快的使用方式 - 无需构建！

```bash
# 1. 设置环境变量
export OPENAI_API_KEY=your_openai_api_key_here

# 2. 使用预构建镜像运行
docker run -d \
  --name graphiti-app \
  -p 7474:7474 \
  -p 7687:7687 \
  -p 8000:8000 \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  ghcr.io/vaenow/graphiti-mcp:latest
```

### 方案二：从源码构建

如果您需要修改代码或本地构建：

#### 1. 设置环境变量
```bash
cp env.example .env
# 编辑 .env 文件，添加你的 OpenAI API Key
```

#### 2. 构建镜像
```bash
docker build -t graphiti-app .
```

#### 3. 运行容器
```bash
docker run -d \
  --name graphiti-app \
  -p 7474:7474 \
  -p 7687:7687 \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your_openai_api_key_here \
  graphiti-app
```

### 访问服务
- Neo4j Browser: http://localhost:7474 (用户名: neo4j, 密码: password)
- 应用日志: `docker logs -f graphiti-app`

## 📦 预构建镜像

我们自动构建并发布多架构 Docker 镜像到 GitHub Container Registry：

- **最新稳定版**: `ghcr.io/vaenow/graphiti-mcp:latest`
- **指定版本**: `ghcr.io/vaenow/graphiti-mcp:v1.0.0`
- **开发版**: `ghcr.io/vaenow/graphiti-mcp:main`

### 支持的架构
- `linux/amd64` (x86_64)
- `linux/arm64` (ARM64/Apple Silicon)

### 镜像标签
- `latest` - 最新稳定版本
- `main` - 最新开发版本
- `v*.*.*` - 具体版本发布
- `v*.*` - 小版本发布
- `v*` - 大版本发布

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

### 基础运行（预构建镜像）
```bash
docker run -d \
  --name graphiti-app \
  -p 7474:7474 \
  -p 7687:7687 \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your_openai_api_key_here \
  ghcr.io/vaenow/graphiti-mcp:latest
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
  ghcr.io/vaenow/graphiti-mcp:latest
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
  ghcr.io/vaenow/graphiti-mcp:latest
```

### 生产环境部署（Docker Compose）
```yaml
version: '3.8'
services:
  graphiti:
    image: ghcr.io/vaenow/graphiti-mcp:latest
    container_name: graphiti-app
    ports:
      - "7474:7474"
      - "7687:7687"
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - graphiti_data:/var/lib/neo4j/data
      - graphiti_logs:/var/lib/neo4j/logs
    restart: unless-stopped

volumes:
  graphiti_data:
  graphiti_logs:
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

## 🛠️ 自定义配置

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
     ghcr.io/vaenow/graphiti-mcp:latest
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
  ghcr.io/vaenow/graphiti-mcp:latest
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

4. **镜像拉取错误**
   ```bash
   # 尝试显式拉取镜像
   docker pull ghcr.io/vaenow/graphiti-mcp:latest
   
   # 或使用指定版本
   docker pull ghcr.io/vaenow/graphiti-mcp:v1.0.0
   ```

### 清理和重启

```bash
# 停止并删除容器
docker stop graphiti-app
docker rm graphiti-app

# 删除本地镜像（如需重新构建）
docker rmi graphiti-app

# 使用预构建镜像
docker run -d \
  --name graphiti-app \
  -p 7474:7474 \
  -p 7687:7687 \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your_openai_api_key_here \
  ghcr.io/vaenow/graphiti-mcp:latest
```

### 数据备份

```bash
# 备份 Neo4j 数据
docker exec graphiti-app neo4j-admin dump --database=neo4j --to=/var/lib/neo4j/data/backup.dump

# 从容器复制备份文件
docker cp graphiti-app:/var/lib/neo4j/data/backup.dump ./backup.dump
```

## 🏗️ 包含的组件

这个 Docker 部署包含：

- **Neo4j 5.26**: 图数据库后端
- **Python 3.11**: 运行时环境
- **Graphiti Core**: 知识图谱框架
- **示例应用**: 开箱即用的 Graphiti 演示和示例数据
- **健康检查**: 容器监控和状态验证
- **数据持久化**: 卷挂载以保持数据

## 🚀 CI/CD 流水线

本仓库包含 GitHub Actions 工作流，自动：

- ✅ 构建多架构 Docker 镜像（AMD64、ARM64）
- ✅ 在每次推送到 `main` 分支时运行
- ✅ 在创建 git 标签时创建版本发布
- ✅ 发布到 GitHub Container Registry
- ✅ 生成安全证明
- ✅ 通过缓存优化构建

### 创建发布版本

要创建新的发布版本：

```bash
git tag v1.0.0
git push origin v1.0.0
```

这将自动触发构建并发布带有版本标签的新镜像。

## 🌍 语言支持

- **中文**: README-CN.md（当前文件）
- **English**: [README.md](README.md)

## 📚 相关资源

- [Graphiti GitHub](https://github.com/getzep/graphiti)
- [Graphiti 文档](https://help.getzep.com/graphiti)
- [Neo4j 文档](https://neo4j.com/docs/)
- [Docker 文档](https://docs.docker.com/)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进这个部署配置！

### 开发工作流

1. Fork 本仓库
2. 创建功能分支
3. 进行修改
4. 使用 `docker build -t test-image .` 进行本地测试
5. 提交 Pull Request

CI 流水线将自动构建和测试您的更改。

## 📄 许可证

本项目遵循与 [Graphiti 项目](https://github.com/getzep/graphiti) 相同的许可证。

---

**愉快地构建知识图谱！** 🎯