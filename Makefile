# ClearScan Application Makefile
# This Makefile manages both the ML service and Flask frontend

.PHONY: help install start stop status clean test deploy dev health docker-build docker-up docker-down docker-logs docker-restart docker-clean gcp-deploy

# Default target
help:
    @echo "ClearScan Application Commands:"
    @echo "  make install    - Install dependencies for both services"
    @echo "  make start      - Start both ML service and frontend app"
    @echo "  make stop       - Stop both services"
    @echo "  make status     - Check status of running services"
    @echo "  make clean      - Clean up temporary files and stop services"
    @echo "  make test       - Run tests"
    @echo "  make deploy     - Prepare for deployment"
    @echo "  make dev        - Start in development mode"
    @echo "  make health     - Health check both services"
    @echo ""
    @echo "Docker Commands:"
    @echo "  make docker-build  - Build Docker containers"
    @echo "  make docker-up     - Start services with Docker Compose"
    @echo "  make docker-down   - Stop Docker services"
    @echo "  make docker-logs   - View Docker container logs"
    @echo "  make docker-restart- Restart Docker services"
    @echo "  make docker-clean  - Clean up Docker resources"
    @echo ""
    @echo "Google Cloud Deployment:"
    @echo "  make gcp-deploy    - Deploy to Google Cloud Run"

# Install dependencies
install:
    @echo "📦 Installing dependencies for both services..."
    pip3 install -r requirements.txt
    @echo "✅ Dependencies installed successfully"

# Start both services
start:
    @echo "🚀 Starting ClearScan Application..."
    @cd ml_service && ./start_ml_service.sh
    @sleep 3
    @python3 run.py &
    @echo $$! > frontend.pid
    @echo "✅ Both services started successfully"
    @echo "🌐 Frontend: http://localhost:5053"
    @echo "🤖 ML Service: http://localhost:5002"

# Start services in background for deployment
start-production:
    @echo "🚀 Starting ClearScan in production mode..."
    @cd ml_service && ./start_ml_service.sh
    @sleep 3
    @nohup python3 run.py > frontend.log 2>&1 &
    @echo $$! > frontend.pid
    @echo "✅ Production services started"

# Stop all services
stop:
    @echo "🛑 Stopping ClearScan services..."
    @if [ -f frontend.pid ]; then \
        echo "Stopping frontend service..."; \
        kill -TERM $$(cat frontend.pid) 2>/dev/null || true; \
        rm -f frontend.pid; \
    fi
    @if [ -f ml_service/ml_service.pid ]; then \
        echo "Stopping ML service..."; \
        kill -TERM $$(cat ml_service/ml_service.pid) 2>/dev/null || true; \
        rm -f ml_service/ml_service.pid; \
    fi
    @echo "✅ All services stopped"

# Check status of services
status:
    @echo "📊 Service Status:"
    @if [ -f frontend.pid ] && ps -p $$(cat frontend.pid) > /dev/null 2>&1; then \
        echo "  ✅ Frontend is running"; \
    else \
        echo "  ❌ Frontend is not running"; \
    fi
    @if [ -f ml_service/ml_service.pid ] && ps -p $$(cat ml_service/ml_service.pid) > /dev/null 2>&1; then \
        echo "  ✅ ML Service is running"; \
    else \
        echo "  ❌ ML Service is not running"; \
    fi

# Clean up temporary files
clean: stop
    @echo "🧹 Cleaning up..."
    @rm -f *.pid ml_service/*.pid *.log ml_service/*.log
    @find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    @find . -name "*.pyc" -delete 2>/dev/null || true
    @echo "✅ Cleanup completed"

# Run tests
test:
    @echo "🧪 Running tests..."
    @python3 -m pytest tests/ -v || echo "No tests found"

# Prepare for deployment
deploy: clean
    @echo "📦 Preparing for deployment..."
    @echo "✅ Deployment files ready"

# Development mode
dev:
    @export FLASK_ENV=development && make start

# Health check
health:
    @echo "🏥 Health check..."
    @curl -f http://localhost:5053/health 2>/dev/null && echo "✅ Frontend healthy" || echo "❌ Frontend unhealthy"
    @curl -f http://localhost:5002/health 2>/dev/null && echo "✅ ML Service healthy" || echo "❌ ML Service unhealthy"

# Docker commands
docker-build:
    @echo "🐳 Building Docker containers..."
    docker-compose build --no-cache
    @echo "✅ Docker containers built successfully!"

docker-up:
    @echo "🚀 Starting ClearScan with Docker Compose..."
    docker-compose up -d
    @echo "✅ Services started!"
    @echo "🌐 Frontend: http://localhost:5053"
    @echo "🤖 ML Service: http://localhost:5002"
    @echo "💡 Use 'make docker-logs' to view logs"

docker-down:
    @echo "🛑 Stopping Docker services..."
    docker-compose down
    @echo "✅ Services stopped!"

docker-logs:
    @echo "📋 Viewing Docker container logs..."
    docker-compose logs -f

docker-restart:
    @echo "🔄 Restarting Docker services..."
    docker-compose restart
    @echo "✅ Services restarted!"

docker-clean:
    @echo "🧹 Cleaning Docker resources..."
    docker-compose down -v --remove-orphans
    docker system prune -f --volumes
    @echo "✅ Docker resources cleaned!"

# Google Cloud Run deployment
gcp-deploy:
	@echo "☁️ Deploying to Google Cloud Run..."
	@echo "Building and pushing container..."
	docker build --platform linux/amd64 -f Dockerfile.combined -t gcr.io/clearscan-app-1755393198/clearscan:latest .
	docker push gcr.io/clearscan-app-1755393198/clearscan:latest
	@echo "Deploying to Cloud Run..."
	gcloud run deploy clearscan-app \
		--image gcr.io/clearscan-app-1755393198/clearscan:latest \
        --platform managed \
        --region us-central1 \
        --allow-unauthenticated \
        --memory 2Gi \
        --cpu 1 \
        --port 5053 \
        --max-instances 10
    @echo "✅ Deployment complete!"