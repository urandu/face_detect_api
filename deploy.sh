#!/bin/bash

# Production deployment script for Face Detection API
# Usage: ./deploy.sh [--build|--restart|--logs|--status]

set -e

COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE=".env"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env file exists
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}Error: $ENV_FILE file not found!${NC}"
    echo "Please copy .env.prod.template to .env and configure it."
    exit 1
fi

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if required environment variables are set
check_env_vars() {
    print_status "Checking environment variables..."
    
    required_vars=(
        "SECRET_KEY"
        "DATABASE_PASSWORD"
        "REDIS_PASSWORD"
        "RABBITMQ_PASSWORD"
        "MINIO_ROOT_PASSWORD"
    )
    
    missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -ne 0 ]; then
        print_error "Missing required environment variables:"
        for var in "${missing_vars[@]}"; do
            echo "  - $var"
        done
        echo "Please configure these in your $ENV_FILE file."
        exit 1
    fi
    
    print_status "Environment variables check passed!"
}

# Function to build and deploy
deploy() {
    print_status "Starting production deployment..."
    
    # Load environment variables
    export $(grep -v '^#' $ENV_FILE | xargs)
    
    # Check environment variables
    check_env_vars
    
    # Build and start services
    print_status "Building and starting services..."
    docker-compose -f $COMPOSE_FILE up -d --build
    
    # Wait a bit for services to start
    print_status "Waiting for services to be ready..."
    sleep 10
    
    # Check service health
    print_status "Checking service health..."
    docker-compose -f $COMPOSE_FILE ps
    
    print_status "Deployment completed!"
    print_status "You can check the status with: ./deploy.sh --status"
    print_status "View logs with: ./deploy.sh --logs"
}

# Function to restart services
restart() {
    print_status "Restarting services..."
    docker-compose -f $COMPOSE_FILE restart
    print_status "Services restarted!"
}

# Function to show logs
show_logs() {
    echo "Following logs... (Ctrl+C to exit)"
    docker-compose -f $COMPOSE_FILE logs -f
}

# Function to show status
show_status() {
    print_status "Service status:"
    docker-compose -f $COMPOSE_FILE ps
    
    print_status "Service health:"
    # Try to check API health
    if curl -s -f http://localhost/health > /dev/null 2>&1; then
        print_status "✓ Nginx health check passed"
    else
        print_warning "✗ Nginx health check failed"
    fi
    
    if curl -s -f http://localhost/api/health/ > /dev/null 2>&1; then
        print_status "✓ API health check passed"
    else
        print_warning "✗ API health check failed"
    fi
}

# Function to stop services
stop() {
    print_status "Stopping services..."
    docker-compose -f $COMPOSE_FILE down
    print_status "Services stopped!"
}

# Function to show help
show_help() {
    echo "Face Detection API Production Deployment Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  --build, -b     Build and deploy the application"
    echo "  --restart, -r   Restart all services"
    echo "  --logs, -l      Show and follow logs"
    echo "  --status, -s    Show service status and health"
    echo "  --stop          Stop all services"
    echo "  --help, -h      Show this help message"
    echo ""
    echo "Environment:"
    echo "  Ensure $ENV_FILE is configured before deployment"
    echo ""
    echo "Examples:"
    echo "  $0 --build      # Deploy the application"
    echo "  $0 --status     # Check if everything is running"
    echo "  $0 --logs       # View application logs"
}

# Main script logic
case "${1:-}" in
    --build|-b)
        deploy
        ;;
    --restart|-r)
        restart
        ;;
    --logs|-l)
        show_logs
        ;;
    --status|-s)
        show_status
        ;;
    --stop)
        stop
        ;;
    --help|-h)
        show_help
        ;;
    "")
        # Default action: deploy
        deploy
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
