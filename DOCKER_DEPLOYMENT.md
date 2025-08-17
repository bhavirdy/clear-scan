# ClearScan Docker Deployment Guide

## Overview
ClearScan has been containerized for easy deployment and scalability. The application consists of two main services:

- **Frontend Service** (Port 5053): Flask web application for medical imaging interface
- **ML Service** (Port 5002): PyTorch-based machine learning service for medical image analysis

## Prerequisites

- Docker and Docker Compose installed
- At least 4GB RAM available for ML service
- GPU support (optional, but recommended for performance)

## Quick Start

### 1. Build and Start Services
```bash
# Build all containers
make docker-build

# Start services in background
make docker-up

# View live logs
make docker-logs
```

### 2. Access Application
- **Frontend Web Interface**: http://localhost:5053
- **ML Service API**: http://localhost:5002
- **Health Checks**: 
  - Frontend: http://localhost:5053/health
  - ML Service: http://localhost:5002/health

## Service Architecture

```
┌─────────────────┐    HTTP Requests    ┌──────────────────┐
│   Frontend      │ ──────────────────→ │   ML Service     │
│   (Port 5053)   │                     │   (Port 5002)    │
└─────────────────┘                     └──────────────────┘
        │                                       │
        ├── Web Interface                       ├── Model Inference
        ├── User Authentication                 ├── GradCAM Generation
        ├── Image Upload Handling               └── Medical Image Processing
        └── Results Display                     
```

## Container Communication

Services communicate through Docker's internal network:
- Frontend → ML Service: `http://ml-service:5002`
- Shared volumes for image uploads and GradCAM outputs
- Health checks ensure service availability before communication

## Environment Configuration

### Frontend Service Environment Variables
```bash
FLASK_ENV=production
FLASK_APP=run.py
FRONTEND_PORT=5053
ML_SERVICE_URL=http://ml-service:5002  # Automatic service discovery
```

### ML Service Environment Variables
```bash
FLASK_ENV=production
FLASK_APP=app.py
ML_SERVICE_PORT=5002
```

## Data Persistence

The deployment uses Docker volumes for data persistence:
- `ml_uploads`: Stores uploaded medical images
- `ml_gradcams`: Stores generated GradCAM visualization images

## Management Commands

### Start/Stop Operations
```bash
# Start all services
make docker-up

# Stop all services
make docker-down

# Restart services
make docker-restart
```

### Monitoring and Debugging
```bash
# View container logs
make docker-logs

# Check container status
docker-compose ps

# Execute shell in container
docker-compose exec frontend bash
docker-compose exec ml-service bash
```

### Cleanup
```bash
# Stop and remove containers with volumes
make docker-clean

# Remove unused Docker resources
docker system prune -a
```

## Production Deployment

### 1. Cloud Platform Deployment
For AWS, GCP, or Azure deployment:
```bash
# Tag images for registry
docker tag clearscan_frontend your-registry/clearscan-frontend:latest
docker tag clearscan_ml-service your-registry/clearscan-ml:latest

# Push to container registry
docker push your-registry/clearscan-frontend:latest
docker push your-registry/clearscan-ml:latest
```

### 2. Load Balancer Configuration
- Frontend service should be behind a load balancer
- ML service can be internal-only with service mesh
- Configure health check endpoints: `/health`

### 3. Resource Requirements
- **Frontend Container**: 512MB RAM, 0.5 CPU
- **ML Container**: 4GB RAM, 2 CPU (8GB+ for optimal performance)
- **Storage**: 20GB+ for model files and image storage

## Security Considerations

### Container Security
- Non-root users in containers
- Read-only model directories
- Minimal base images (Python 3.9-slim)
- No unnecessary packages or services

### Network Security
- Internal service communication only
- Frontend exposed only on necessary port
- No direct ML service external access

### Data Security
- Temporary file cleanup
- Secure file upload handling
- Input validation on all endpoints

## Troubleshooting

### Common Issues

**Service Communication Errors**
```bash
# Check network connectivity
docker-compose exec frontend ping ml-service

# Verify service discovery
docker-compose exec frontend curl http://ml-service:5002/health
```

**ML Service Memory Issues**
```bash
# Check container resources
docker stats

# Increase memory limits in docker-compose.yml if needed
```

**Volume Mount Issues**
```bash
# Check volume permissions
docker-compose exec ml-service ls -la /app/uploads
docker-compose exec ml-service ls -la /app/gradcams
```

### Logs and Debugging
```bash
# Individual service logs
docker-compose logs frontend
docker-compose logs ml-service

# Follow specific service logs
docker-compose logs -f ml-service
```

## Performance Optimization

### ML Service Optimization
- Use GPU-enabled base images if available
- Implement model caching
- Configure appropriate worker processes

### Frontend Optimization
- Enable request caching
- Optimize static file serving
- Configure appropriate concurrent connections

## Backup and Recovery

### Model Files
```bash
# Backup model files
docker cp clearscan-ml-service:/app/models ./model-backup/
```

### Persistent Data
```bash
# Backup volumes
docker run --rm -v ml_uploads:/data -v $(pwd):/backup alpine tar czf /backup/uploads-backup.tar.gz -C /data .
docker run --rm -v ml_gradcams:/data -v $(pwd):/backup alpine tar czf /backup/gradcams-backup.tar.gz -C /data .
```

## Support

For deployment issues:
1. Check container logs: `make docker-logs`
2. Verify health endpoints are responding
3. Ensure adequate system resources
4. Review Docker Compose configuration

The containerized deployment maintains full compatibility with the existing codebase while providing cloud-ready deployment capabilities.
