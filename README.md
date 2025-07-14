# Graphiti Docker Deployment Guide

A comprehensive Docker deployment solution for [Graphiti](https://github.com/getzep/graphiti) knowledge graphs, including Neo4j database and Graphiti application in a containerized environment.

[中文文档](README-CN.md) | **English**

## 📋 Prerequisites

- Docker
- OpenAI API Key

## 🚀 Quick Start

### 1. Set Environment Variables
```bash
cp env.example .env
# Edit the .env file and add your OpenAI API Key
```

### 2. Build the Image
```bash
docker build -t graphiti-app .
```

### 3. Run the Container
```bash
docker run -d \
  --name graphiti-app \
  -p 7474:7474 \
  -p 7687:7687 \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your_openai_api_key_here \
  graphiti-app
```

### 4. Access Services
- Neo4j Browser: http://localhost:7474 (Username: neo4j, Password: password)
- Application logs: `docker logs -f graphiti-app`

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

### Basic Deployment
```bash
docker run -d \
  --name graphiti-app \
  -p 7474:7474 \
  -p 7687:7687 \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your_openai_api_key_here \
  graphiti-app
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
  graphiti-app
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
  graphiti-app
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
     graphiti-app
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
  graphiti-app
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

### Cleanup and Restart

```bash
# Stop and remove container
docker stop graphiti-app
docker rm graphiti-app

# Remove image (if rebuilding is needed)
docker rmi graphiti-app

# Rebuild and run
docker build -t graphiti-app .
docker run -d \
  --name graphiti-app \
  -p 7474:7474 \
  -p 7687:7687 \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your_openai_api_key_here \
  graphiti-app
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

## 🌍 Language Support

- **English**: README.md (This file)
- **中文**: [README-CN.md](README-CN.md)

## 📚 Related Resources

- [Graphiti GitHub Repository](https://github.com/getzep/graphiti)
- [Graphiti Documentation](https://help.getzep.com/graphiti)
- [Neo4j Documentation](https://neo4j.com/docs/)
- [Docker Documentation](https://docs.docker.com/)

## 🤝 Contributing

We welcome Issues and Pull Requests to improve this deployment configuration!

## 📄 License

This project follows the same license as the [Graphiti project](https://github.com/getzep/graphiti).

---

**Happy Graphing!** 🎯