# Docker Configuration

This directory contains Docker-related files for containerized deployment.

## Files

- `Dockerfile` - Container image definition
- `docker-compose.yml` - Multi-container orchestration

## Usage

```bash
# Build image
docker build -t llama-gpu -f docker/Dockerfile .

# Run with docker-compose
docker-compose -f docker/docker-compose.yml up
```

## Requirements

- Docker 20.10+
- Docker Compose 2.0+
- NVIDIA Docker (for GPU support)

## GPU Support

For GPU acceleration in containers:
```bash
docker run --gpus all llama-gpu
```
