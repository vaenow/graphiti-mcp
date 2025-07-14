# Graphiti Docker Deployment Guide

A comprehensive Docker deployment solution for [Graphiti](https://github.com/getzep/graphiti) knowledge graphs, including Neo4j database and Graphiti application in a containerized environment.

[中文文档](README-CN.md) | **English**

[![Docker Build](https://github.com/USERNAME/REPO/actions/workflows/docker-build.yml/badge.svg)](https://github.com/USERNAME/REPO/actions/workflows/docker-build.yml)
[![Docker Image](https://img.shields.io/badge/docker-ghcr.io-blue.svg)](https://ghcr.io/USERNAME/REPO)

## 📋 Prerequisites

- Docker
- OpenAI API Key

## 🚀 Quick Start

### Option 1: Use Pre-built Image (Recommended)

The fastest way to get started - no building required!

```bash
# 1. Set environment variable
export OPENAI_API_KEY=your_openai_api_key_here

# 2. Run with pre-built image
docker run -d \
  --name graphiti-app \
  -p 7474:7474 \
  -p 7687:7687 \
  -p 8000:8000 \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  ghcr.io/USERNAME/REPO:latest
```

### Option 2: Build from Source

If you want to modify the code or build locally:

#### 1. Set Environment Variables
```bash
cp env.example .env
# Edit the .env file and add your OpenAI API Key
```

#### 2. Build the Image
```bash
docker build -t graphiti-app .
```

#### 3. Run the Container
```bash
docker run -d \
  --name graphiti-app \
  -p 7474:7474 \
  -p 7687:7687 \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your_openai_api_key_here \
  graphiti-app
```

### Access Services
- Neo4j Browser: http://localhost:7474 (Username: neo4j, Password: password)
- Application logs: `docker logs -f graphiti-app`

## 📦 Pre-built Images

We automatically build and publish multi-architecture Docker images to GitHub Container Registry:

- **Latest stable**: `ghcr.io/USERNAME/REPO:latest`
- **Specific version**: `ghcr.io/USERNAME/REPO:v1.0.0`
- **Development**: `ghcr.io/USERNAME/REPO:main`

### Supported Architectures
- `linux/amd64` (x86_64)
- `linux/arm64` (ARM64/Apple Silicon)

### Image Tags
- `latest` - Latest stable release
- `main` - Latest development build
- `v*.*.*` - Specific version releases
- `v*.*` - Minor version releases
- `v*` - Major version releases

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default Value |
|----------|-------------|---------------|
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `NEO4J_URI` | Neo4j connection URI | `bolt://localhost:7687` |
| `NEO4J_USER` | Neo4j username | `neo4j` |
| `NEO4J_PASSWORD` | Neo4j password | `password` |
| `USE_PARALLEL_RUNTIME` | Enable Neo4j parallel runtime | `false` |
| `GRAPHITI_TELEMETRY_ENABLED` | Enable telemetry | `true` |

### Ports

- **7474**: Neo4j HTTP interface
- **7687**: Neo4j Bolt protocol
- **8000**: Graphiti application port

## 🔧 Deployment Options

### Basic Deployment (Pre-built Image)
```bash
docker run -d \
  --name graphiti-app \
  -p 7474:7474 \
  -p 7687:7687 \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your_openai_api_key_here \
  ghcr.io/USERNAME/REPO:latest
```

### Development Mode (Mount Code Directory)
```bash
docker run -d \
  --name graphiti-app \
  -p 7474:7474 \
  -p 7687:7687 \
  -p 8000:8000 \
  -v $(pwd):/app \
  -e OPENAI_API_KEY=your_openai_api_key_here \
  ghcr.io/USERNAME/REPO:latest
```

### Data Persistence
```bash
docker run -d \
  --name graphiti-app \
  -p 7474:7474 \
  -p 7687:7687 \
  -p 8000:8000 \
  -v graphiti_data:/var/lib/neo4j/data \
  -v graphiti_logs:/var/lib/neo4j/logs \
  -e OPENAI_API_KEY=your_openai_api_key_here \
  ghcr.io/USERNAME/REPO:latest
```

### Production Deployment with Docker Compose
```yaml
version: '3.8'
services:
  graphiti:
    image: ghcr.io/USERNAME/REPO:latest
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

## 📊 Monitoring and Logging

### View Logs
```bash
# Application logs
docker logs -f graphiti-app

# Enter container for detailed logs
docker exec -it graphiti-app bash
```

### Health Checks
```bash
# Check Neo4j status
curl http://localhost:7474/

# Check container status
docker ps
```

## 🛠️ Custom Configuration

### Neo4j Configuration

To customize Neo4j configuration:

1. Create a `neo4j.conf` file
2. Mount the configuration file when running:
   ```bash
   docker run -d \
     --name graphiti-app \
     -p 7474:7474 \
     -p 7687:7687 \
     -p 8000:8000 \
     -v $(pwd)/neo4j.conf:/etc/neo4j/neo4j.conf \
     -e OPENAI_API_KEY=your_openai_api_key_here \
     ghcr.io/USERNAME/REPO:latest
   ```

### Application Code

- `main.py`: Main application file containing Graphiti example code
- Modify this file to implement your business logic as needed

## 📈 Performance Optimization

### Memory Settings

Adjust Neo4j memory usage through environment variables:

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
  ghcr.io/USERNAME/REPO:latest
```

## 🔍 Troubleshooting

### Common Issues

1. **Container startup failure**
   ```bash
   # View detailed error information
   docker logs graphiti-app
   ```

2. **Unable to connect to Neo4j**
   ```bash
   # Check Neo4j service status
   docker exec -it graphiti-app neo4j status
   ```

3. **OpenAI API errors**
   - Verify API key is set correctly
   - Check network connectivity

4. **Image pull errors**
   ```bash
   # Try pulling the image explicitly
   docker pull ghcr.io/USERNAME/REPO:latest
   
   # Or use a specific version
   docker pull ghcr.io/USERNAME/REPO:v1.0.0
   ```

### Cleanup and Restart

```bash
# Stop and remove container
docker stop graphiti-app
docker rm graphiti-app

# Remove local image (if rebuilding is needed)
docker rmi graphiti-app

# Using pre-built image
docker run -d \
  --name graphiti-app \
  -p 7474:7474 \
  -p 7687:7687 \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your_openai_api_key_here \
  ghcr.io/USERNAME/REPO:latest
```

### Data Backup

```bash
# Backup Neo4j data
docker exec graphiti-app neo4j-admin dump --database=neo4j --to=/var/lib/neo4j/data/backup.dump

# Copy backup file from container
docker cp graphiti-app:/var/lib/neo4j/data/backup.dump ./backup.dump
```

## 🏗️ What's Included

This Docker deployment includes:

- **Neo4j 5.26**: Graph database backend
- **Python 3.11**: Runtime environment
- **Graphiti Core**: Knowledge graph framework
- **Example Application**: Ready-to-run Graphiti demo with sample data
- **Health Checks**: Container monitoring and status verification
- **Data Persistence**: Volume mounting for data preservation

## 🚀 CI/CD Pipeline

This repository includes GitHub Actions workflow that automatically:

- ✅ Builds multi-architecture Docker images (AMD64, ARM64)
- ✅ Runs on every push to `main` branch
- ✅ Creates versioned releases on git tags
- ✅ Publishes to GitHub Container Registry
- ✅ Generates security attestations
- ✅ Optimizes builds with caching

### Creating a Release

To create a new release:

```bash
git tag v1.0.0
git push origin v1.0.0
```

This will automatically trigger the build and publish a new image with version tags.

## 🌍 Language Support

- **English**: README.md (This file)
- **中文**: [README-CN.md](README-CN.md)

## 📚 Related Resources

- [Graphiti GitHub Repository](https://github.com/getzep/graphiti)
- [Graphiti Documentation](https://help.getzep.com/graphiti)
- [Neo4j Documentation](https://neo4j.com/docs/)
- [Docker Documentation](https://docs.docker.com/)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)

## 🤝 Contributing

We welcome Issues and Pull Requests to improve this deployment configuration!

### Development Workflow

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally with `docker build -t test-image .`
5. Submit a pull request

The CI pipeline will automatically build and test your changes.

## 📄 License

This project follows the same license as the [Graphiti project](https://github.com/getzep/graphiti).

---

**Happy Graphing!** 🎯