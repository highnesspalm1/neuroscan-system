# NeuroScan Docker Management
# Use PowerShell commands for Windows compatibility

.DEFAULT_GOAL := help

# Variables
COMPOSE_FILE = docker-compose.yml
COMPOSE_PROD_FILE = docker-compose.prod.yml
PROJECT_NAME = neuroscan

.PHONY: help build up down logs ps clean restart backup restore test

help: ## Show this help message
	@echo "NeuroScan Docker Management Commands:"
	@echo ""
	@echo "Development Commands:"
	@echo "  make build       - Build all Docker images"
	@echo "  make up          - Start all services in development mode"
	@echo "  make down        - Stop all services"
	@echo "  make restart     - Restart all services"
	@echo "  make logs        - Show logs from all services"
	@echo "  make ps          - Show running containers"
	@echo ""
	@echo "Production Commands:"
	@echo "  make prod-up     - Start all services in production mode"
	@echo "  make prod-down   - Stop production services"
	@echo "  make prod-logs   - Show production logs"
	@echo ""
	@echo "Database Commands:"
	@echo "  make backup      - Create database backup"
	@echo "  make restore     - Restore database from backup"
	@echo "  make db-migrate  - Run database migrations"
	@echo ""
	@echo "Maintenance Commands:"
	@echo "  make clean       - Remove all containers and volumes"
	@echo "  make test        - Run all tests"
	@echo "  make health      - Check service health"

build: ## Build all Docker images
	docker-compose -f $(COMPOSE_FILE) build --no-cache

up: ## Start all services in development mode
	docker-compose -f $(COMPOSE_FILE) up -d
	@echo "Services started. Access the application at:"
	@echo "  Frontend: http://localhost:3000"
	@echo "  Backend API: http://localhost:8000"
	@echo "  Backend Docs: http://localhost:8000/docs"

down: ## Stop all services
	docker-compose -f $(COMPOSE_FILE) down

restart: ## Restart all services
	docker-compose -f $(COMPOSE_FILE) restart

logs: ## Show logs from all services
	docker-compose -f $(COMPOSE_FILE) logs -f

ps: ## Show running containers
	docker-compose -f $(COMPOSE_FILE) ps

# Production Commands
prod-build: ## Build production images
	docker-compose -f $(COMPOSE_PROD_FILE) build --no-cache

prod-up: ## Start all services in production mode
	docker-compose -f $(COMPOSE_PROD_FILE) up -d
	@echo "Production services started."
	@echo "Access the application at: http://localhost"

prod-down: ## Stop production services
	docker-compose -f $(COMPOSE_PROD_FILE) down

prod-logs: ## Show production logs
	docker-compose -f $(COMPOSE_PROD_FILE) logs -f

# Database Commands
backup: ## Create database backup
	docker-compose -f $(COMPOSE_FILE) exec postgres /backup.sh

restore: ## Restore database from backup (requires BACKUP_FILE environment variable)
	@if [ -z "$(BACKUP_FILE)" ]; then \
		echo "Error: BACKUP_FILE environment variable is required"; \
		echo "Usage: make restore BACKUP_FILE=backup_filename.sql.gz"; \
		exit 1; \
	fi
	docker-compose -f $(COMPOSE_FILE) exec postgres /restore.sh $(BACKUP_FILE)

db-migrate: ## Run database migrations
	docker-compose -f $(COMPOSE_FILE) exec backend alembic upgrade head

# Maintenance Commands
clean: ## Remove all containers, networks, and volumes
	docker-compose -f $(COMPOSE_FILE) down -v --remove-orphans
	docker-compose -f $(COMPOSE_PROD_FILE) down -v --remove-orphans
	docker system prune -f
	@echo "All containers, networks, and volumes removed."

test: ## Run all tests
	docker-compose -f $(COMPOSE_FILE) exec backend python -m pytest tests/ -v
	@echo "All tests completed."

health: ## Check service health
	@echo "Checking service health..."
	@docker-compose -f $(COMPOSE_FILE) ps
	@echo ""
	@echo "Backend health:"
	@curl -f http://localhost:8000/health || echo "Backend not responding"
	@echo ""
	@echo "Frontend health:"
	@curl -f http://localhost:3000 || echo "Frontend not responding"

# Development helpers
shell-backend: ## Open shell in backend container
	docker-compose -f $(COMPOSE_FILE) exec backend /bin/bash

shell-frontend: ## Open shell in frontend container
	docker-compose -f $(COMPOSE_FILE) exec frontend /bin/sh

shell-db: ## Open PostgreSQL shell
	docker-compose -f $(COMPOSE_FILE) exec postgres psql -U neuroscan -d neuroscan_db

# Quick setup for new developers
setup: ## Complete setup for new developers
	@echo "Setting up NeuroScan development environment..."
	cp .env.example .env
	@echo "Please edit .env file with your configuration"
	make build
	make up
	make db-migrate
	@echo "Setup complete! Access the application at http://localhost:3000"
