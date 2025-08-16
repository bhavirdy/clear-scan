# Google Cloud Run Deployment Guide

## Prerequisites
- Google Cloud SDK installed (`gcloud`)
- Project with billing enabled

## Step 1: Setup and Authentication
```bash
# Login and set project
gcloud auth login
gcloud config set project your-project-id
gcloud auth configure-docker
```

## Step 2: Deploy ML Service
```bash
# Tag for Google Container Registry
docker tag clear-scan-ml-service:latest gcr.io/your-project-id/clearscan-ml:latest

# Push to GCR
docker push gcr.io/your-project-id/clearscan-ml:latest

# Deploy to Cloud Run
gcloud run deploy clearscan-ml \
  --image gcr.io/your-project-id/clearscan-ml:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 4Gi \
  --cpu 2 \
  --port 5002 \
  --max-instances 10
```

## Step 3: Deploy Frontend Service
```bash
# Tag and push frontend
docker tag clear-scan-frontend:latest gcr.io/your-project-id/clearscan-frontend:latest
docker push gcr.io/your-project-id/clearscan-frontend:latest

# Get ML service URL
ML_SERVICE_URL=$(gcloud run services describe clearscan-ml --region us-central1 --format 'value(status.url)')

# Deploy frontend with ML service URL
gcloud run deploy clearscan-frontend \
  --image gcr.io/your-project-id/clearscan-frontend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --port 5053 \
  --set-env-vars ML_SERVICE_URL=$ML_SERVICE_URL
```

## Step 4: Get Application URL
```bash
# Get frontend URL
gcloud run services describe clearscan-frontend --region us-central1 --format 'value(status.url)'
```

**Pros**:
- ✅ Serverless (pay per request)
- ✅ Auto-scaling to zero
- ✅ HTTPS included
- ✅ Global CDN
- ✅ Simple deployment

**Cons**:
- ❌ Cold starts (3-5 seconds)
- ❌ No persistent storage
- ❌ Request timeout limits (60 minutes)

**Cost**: ~$10-30/month for moderate usage
**Best for**: Development, demos, low-traffic production
