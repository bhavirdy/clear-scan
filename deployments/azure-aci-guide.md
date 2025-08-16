# Azure Container Instances Deployment Guide

## Prerequisites
- Azure CLI installed (`az`)
- Azure subscription

## Step 1: Setup Azure Resources
```bash
# Login to Azure
az login

# Create resource group
az group create --name clearscan-rg --location eastus

# Create container registry
az acr create --resource-group clearscan-rg --name clearscancr --sku Basic
az acr login --name clearscancr
```

## Step 2: Push Images to ACR
```bash
# Tag images for ACR
docker tag clear-scan-ml-service:latest clearscancr.azurecr.io/clearscan-ml:latest
docker tag clear-scan-frontend:latest clearscancr.azurecr.io/clearscan-frontend:latest

# Push images
docker push clearscancr.azurecr.io/clearscan-ml:latest
docker push clearscancr.azurecr.io/clearscan-frontend:latest
```

## Step 3: Create Container Group with YAML
```yaml
# container-group.yaml
apiVersion: 2021-09-01
location: eastus
name: clearscan-group
properties:
  containers:
  - name: ml-service
    properties:
      image: clearscancr.azurecr.io/clearscan-ml:latest
      resources:
        requests:
          cpu: 2.0
          memoryInGb: 4.0
      ports:
      - port: 5002
  - name: frontend
    properties:
      image: clearscancr.azurecr.io/clearscan-frontend:latest
      resources:
        requests:
          cpu: 1.0
          memoryInGb: 2.0
      ports:
      - port: 5053
      environmentVariables:
      - name: ML_SERVICE_URL
        value: http://localhost:5002
  osType: Linux
  restartPolicy: Always
  ipAddress:
    type: Public
    ports:
    - protocol: tcp
      port: 5053
  imageRegistryCredentials:
  - server: clearscancr.azurecr.io
    username: clearscancr
    password: <registry-password>
tags: {}
type: Microsoft.ContainerInstance/containerGroups
```

## Step 4: Deploy Container Group
```bash
# Get ACR credentials
az acr credential show --name clearscancr

# Deploy container group
az container create --resource-group clearscan-rg --file container-group.yaml

# Get public IP
az container show --resource-group clearscan-rg --name clearscan-group --query ipAddress.ip --output tsv
```

**Cost**: ~$40-80/month
**Scaling**: Manual scaling
**Storage**: Persistent file shares available
