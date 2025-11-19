#!/bin/bash

# CTF SQL Injection Service - Deployment Script
# This script automates the deployment process

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SERVICE_NAME="ctf-sqli-service"
PORT=5050

# Functions
print_banner() {
    echo -e "${BLUE}"
    echo "======================================"
    echo "  CTF SQL Injection Service"
    echo "  Deployment Script"
    echo "======================================"
    echo -e "${NC}"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[*]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

check_dependencies() {
    print_info "Checking dependencies..."

    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi
    print_success "Docker found"

    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not installed"
        exit 1
    fi
    print_success "Docker Compose found"
}

check_port() {
    print_info "Checking if port $PORT is available..."

    if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        print_warning "Port $PORT is already in use"
        read -p "Do you want to continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        print_success "Port $PORT is available"
    fi
}

build_service() {
    print_info "Building Docker image..."
    docker-compose build
    print_success "Docker image built successfully"
}

start_service() {
    print_info "Starting service..."
    docker-compose up -d
    print_success "Service started"
}

wait_for_service() {
    print_info "Waiting for service to be ready..."

    max_attempts=30
    attempt=0

    while [ $attempt -lt $max_attempts ]; do
        if curl -s http://localhost:$PORT/health > /dev/null 2>&1; then
            print_success "Service is ready"
            return 0
        fi

        attempt=$((attempt + 1))
        echo -n "."
        sleep 1
    done

    echo
    print_error "Service failed to start within timeout"
    print_info "Check logs with: docker-compose logs"
    return 1
}

verify_service() {
    print_info "Verifying service..."

    response=$(curl -s http://localhost:$PORT/health)
    if [ "$response" = "OK" ]; then
        print_success "Service health check passed"
    else
        print_error "Service health check failed"
        return 1
    fi

    # Test basic functionality
    if curl -s "http://localhost:$PORT/search?id=1" | grep -q "User Found"; then
        print_success "Basic functionality verified"
    else
        print_error "Basic functionality test failed"
        return 1
    fi
}

show_info() {
    echo
    echo -e "${GREEN}======================================"
    echo "  Service Deployed Successfully!"
    echo -e "======================================${NC}"
    echo
    echo "Service URL: http://localhost:$PORT"
    echo "Health check: http://localhost:$PORT/health"
    echo
    echo -e "${YELLOW}Important for organizers:${NC}"
    echo "  - Flag: centralctf{bl1nd_5ql_w1th_w4f_byp4ss_m4st3r}"
    echo "  - Run exploit: python3 exploit.py"
    echo "  - View logs: docker-compose logs -f"
    echo
    echo -e "${YELLOW}DO NOT share these files with participants:${NC}"
    echo "  - SOLUTION.md"
    echo "  - exploit.py"
    echo "  - MANUAL_TESTING.md"
    echo
    echo "Management commands:"
    echo "  Stop:    docker-compose down"
    echo "  Restart: docker-compose restart"
    echo "  Logs:    docker-compose logs -f"
    echo
}

cleanup() {
    print_info "Cleaning up old containers and data..."
    docker-compose down -v 2>/dev/null || true
    rm -rf data/
    print_success "Cleanup complete"
}

# Main script
main() {
    print_banner

    # Parse arguments
    case "${1:-}" in
        clean)
            cleanup
            exit 0
            ;;
        stop)
            print_info "Stopping service..."
            docker-compose down
            print_success "Service stopped"
            exit 0
            ;;
        restart)
            print_info "Restarting service..."
            docker-compose restart
            print_success "Service restarted"
            exit 0
            ;;
        logs)
            docker-compose logs -f
            exit 0
            ;;
        status)
            docker-compose ps
            exit 0
            ;;
        rebuild)
            print_info "Rebuilding and restarting..."
            docker-compose down
            docker-compose up -d --build
            wait_for_service
            verify_service
            show_info
            exit 0
            ;;
        help|--help|-h)
            echo "Usage: $0 [command]"
            echo
            echo "Commands:"
            echo "  (none)   - Deploy the service (default)"
            echo "  clean    - Remove containers and data"
            echo "  stop     - Stop the service"
            echo "  restart  - Restart the service"
            echo "  logs     - View service logs"
            echo "  status   - Show service status"
            echo "  rebuild  - Rebuild and restart"
            echo "  help     - Show this help message"
            exit 0
            ;;
    esac

    # Default: Deploy
    check_dependencies
    check_port
    build_service
    start_service
    wait_for_service

    if verify_service; then
        show_info
    else
        print_error "Deployment verification failed"
        print_info "Check logs with: docker-compose logs"
        exit 1
    fi
}

# Run main function
main "$@"
