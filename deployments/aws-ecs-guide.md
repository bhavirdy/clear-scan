# AWS ECS Deployment Guide

## Prerequisites
- AWS CLI configured (`aws configure`)
- Docker images pushed to ECR (Elastic Container Registry)

## Step 1: Create ECR Repositories
```bash
# Create repositories
aws ecr create-repository --repository-name clearscan-frontend --region us-east-1
aws ecr create-repository --repository-name clearscan-ml-service --region us-east-1

# Get login token
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <your-account-id>.dkr.ecr.us-east-1.amazonaws.com
```

## Step 2: Tag and Push Images
```bash
# Tag images for ECR
docker tag clear-scan-frontend:latest <your-account-id>.dkr.ecr.us-east-1.amazonaws.com/clearscan-frontend:latest
docker tag clear-scan-ml-service:latest <your-account-id>.dkr.ecr.us-east-1.amazonaws.com/clearscan-ml-service:latest

# Push images
docker push <your-account-id>.dkr.ecr.us-east-1.amazonaws.com/clearscan-frontend:latest
docker push <your-account-id>.dkr.ecr.us-east-1.amazonaws.com/clearscan-ml-service:latest
```

## Step 3: Deploy with ECS Task Definition
```json
{
  "family": "clearscan-task",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "2048",
  "memory": "4096",
  "executionRoleArn": "arn:aws:iam::<account-id>:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "ml-service",
      "image": "<your-account-id>.dkr.ecr.us-east-1.amazonaws.com/clearscan-ml-service:latest",
      "memory": 3072,
      "essential": true,
      "portMappings": [{"containerPort": 5002}],
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:5002/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3
      }
    },
    {
      "name": "frontend",
      "image": "<your-account-id>.dkr.ecr.us-east-1.amazonaws.com/clearscan-frontend:latest",
      "memory": 1024,
      "essential": true,
      "portMappings": [{"containerPort": 5053, "protocol": "tcp"}],
      "environment": [
        {"name": "ML_SERVICE_URL", "value": "http://localhost:5002"}
      ],
      "dependsOn": [{"containerName": "ml-service", "condition": "HEALTHY"}],
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:5053/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3
      }
    }
  ]
}
```

## Step 4: Create ECS Service
```bash
# Create cluster
aws ecs create-cluster --cluster-name clearscan-cluster

# Register task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json

# Create service with load balancer
aws ecs create-service \
  --cluster clearscan-cluster \
  --service-name clearscan-service \
  --task-definition clearscan-task:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx,subnet-yyy],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

**Cost**: ~$50-100/month for small-medium usage
**Scaling**: Auto-scaling based on CPU/memory
**Management**: Fully managed by AWS
