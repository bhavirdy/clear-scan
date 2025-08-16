# ClearScan Application Makefile
# This Makefile manages both the ML service and Flask frontend

.PHONY: help install start stop status clean test deploy

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

# Install dependencies
install:
	@echo "📦 Installing dependencies for both services..."
	@echo "Installing frontend dependencies..."
	pip3 install -r requirements.txt
	@echo "Installing ML service dependencies..."
	cd ml_service && pip3 install -r requirements.txt
	@echo "✅ Dependencies installed successfully"

# Start both services
start:
	@echo "🚀 Starting ClearScan Application..."
	@echo "Starting ML service..."
	@cd ml_service && ./start_ml_service.sh
	@sleep 3
	@echo "Starting Flask frontend..."
	@echo "Frontend will start on port specified by PORT env var (default: 8000)"
	@python3 application.py &
	@echo $$! > frontend.pid
	@echo "✅ Both services started successfully"
	@echo "🌐 Frontend: http://localhost:$${PORT:-8000}"
	@echo "🤖 ML Service: http://localhost:5002"

# Start services in background for deployment
start-production:
	@echo "🚀 Starting ClearScan in production mode..."
	@cd ml_service && ./start_ml_service.sh
	@sleep 3
	@nohup python3 application.py > frontend.log 2>&1 &
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
	@echo "Frontend Service:"
	@if [ -f frontend.pid ] && ps -p $$(cat frontend.pid) > /dev/null 2>&1; then \
		echo "  ✅ Frontend is running (PID: $$(cat frontend.pid))"; \
	else \
		echo "  ❌ Frontend is not running"; \
	fi
	@echo "ML Service:"
	@if [ -f ml_service/ml_service.pid ] && ps -p $$(cat ml_service/ml_service.pid) > /dev/null 2>&1; then \
		echo "  ✅ ML Service is running (PID: $$(cat ml_service/ml_service.pid))"; \
	else \
		echo "  ❌ ML Service is not running"; \
	fi

# Clean up temporary files
clean: stop
	@echo "🧹 Cleaning up..."
	@rm -f *.pid
	@rm -f ml_service/*.pid
	@rm -f *.log
	@rm -f ml_service/*.log
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ Cleanup completed"

# Run tests
test:
	@echo "🧪 Running tests..."
	@python3 -m pytest tests/ -v || echo "No tests found or tests failed"

# Prepare for deployment
deploy: clean
	@echo "📦 Preparing for deployment..."
	@echo "Checking required files..."
	@test -f application.py || (echo "❌ application.py not found" && exit 1)
	@test -f requirements.txt || (echo "❌ requirements.txt not found" && exit 1)
	@test -d .ebextensions || (echo "❌ .ebextensions directory not found" && exit 1)
	@echo "✅ Deployment files ready"
	@echo "💡 Run 'eb deploy' to deploy to Elastic Beanstalk"

# Development mode - start with auto-reload
dev:
	@echo "🔧 Starting in development mode..."
	@export FLASK_ENV=development && make start

# Check health of services
health:
	@echo "🏥 Health check..."
	@curl -f http://localhost:$${PORT:-8000}/health 2>/dev/null && echo "✅ Frontend healthy" || echo "❌ Frontend unhealthy"
	@curl -f http://localhost:5002/health 2>/dev/null && echo "✅ ML Service healthy" || echo "❌ ML Service unhealthy"

# Docker deployment commands
docker-build:
	@echo "🐳 Building Docker containers..."
	docker-compose build --no-cache
	@echo "✅ Docker containers built successfully!"

docker-up:
	@echo "🚀 Starting ClearScan services with Docker Compose..."
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
	make docker-down
	make docker-up

docker-clean:
	@echo "🧹 Cleaning up Docker resources..."
	docker-compose down -v --remove-orphans
	docker system prune -f
	@echo "✅ Cleanup complete!"

# Docker deployment commands
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
	docker-compose down -v
	docker system prune -f
	@echo "✅ Docker resources cleaned!"
