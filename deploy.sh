#!/bin/bash

###############################################################################
# Email Validator Pro - Deployment Script for Ubuntu Server
# Version: 3.0.0
# 
# This script automates the deployment process:
# - Installs Docker and Docker Compose
# - Sets up the application
# - Configures firewall
# - Starts the service
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  Email Validator Pro - Deployment Script               ║${NC}"
    echo -e "${BLUE}║  Version 3.0.0                                          ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Check if running as root
check_root() {
    if [ "$EUID" -ne 0 ]; then 
        print_error "Please run as root (use sudo)"
        exit 1
    fi
    print_success "Running with root privileges"
}

# Check Ubuntu version
check_ubuntu() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        if [[ "$ID" != "ubuntu" ]]; then
            print_warning "This script is designed for Ubuntu. Your OS: $ID"
            read -p "Continue anyway? (y/n) " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                exit 1
            fi
        else
            print_success "Ubuntu detected: $VERSION"
        fi
    fi
}

# Update system
update_system() {
    print_info "Updating system packages..."
    apt-get update -qq
    apt-get upgrade -y -qq
    print_success "System updated"
}

# Install Docker
install_docker() {
    if command -v docker &> /dev/null; then
        print_success "Docker already installed: $(docker --version)"
        return
    fi

    print_info "Installing Docker..."
    
    # Install prerequisites
    apt-get install -y -qq \
        apt-transport-https \
        ca-certificates \
        curl \
        gnupg \
        lsb-release

    # Add Docker's official GPG key
    mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg

    # Set up Docker repository
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

    # Install Docker Engine
    apt-get update -qq
    apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    # Start and enable Docker
    systemctl start docker
    systemctl enable docker

    print_success "Docker installed successfully"
}

# Install Docker Compose (standalone)
install_docker_compose() {
    if command -v docker-compose &> /dev/null; then
        print_success "Docker Compose already installed: $(docker-compose --version)"
        return
    fi

    print_info "Installing Docker Compose..."
    
    DOCKER_COMPOSE_VERSION="2.23.0"
    curl -L "https://github.com/docker/compose/releases/download/v${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" \
        -o /usr/local/bin/docker-compose
    
    chmod +x /usr/local/bin/docker-compose
    
    print_success "Docker Compose installed successfully"
}

# Configure firewall
configure_firewall() {
    print_info "Configuring firewall..."
    
    if command -v ufw &> /dev/null; then
        # Allow SSH
        ufw allow 22/tcp comment 'SSH'
        
        # Allow HTTP/HTTPS
        ufw allow 80/tcp comment 'HTTP'
        ufw allow 443/tcp comment 'HTTPS'
        
        # Allow application port
        ufw allow 5000/tcp comment 'Email Validator Pro'
        
        # Enable firewall
        ufw --force enable
        
        print_success "Firewall configured"
    else
        print_warning "UFW not found, skipping firewall configuration"
    fi
}

# Setup application
setup_application() {
    print_info "Setting up application..."
    
    APP_DIR="/opt/email-validator-pro"
    
    # Create application directory if not exists
    if [ ! -d "$APP_DIR" ]; then
        mkdir -p "$APP_DIR"
        print_success "Created application directory: $APP_DIR"
    fi
    
    # Copy files if we're not already in the app directory
    CURRENT_DIR=$(pwd)
    if [ "$CURRENT_DIR" != "$APP_DIR" ]; then
        print_info "Copying application files to $APP_DIR..."
        cp -r . "$APP_DIR/"
        cd "$APP_DIR"
    fi
    
    # Create logs directory
    mkdir -p logs
    chmod 755 logs
    
    # Create .env file if not exists
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_success "Created .env file from .env.example"
        fi
    fi
    
    print_success "Application setup complete"
}

# Build and start containers
start_application() {
    print_info "Building and starting containers..."
    
    # Stop existing containers
    docker-compose down 2>/dev/null || true
    
    # Build images
    docker-compose build
    
    # Start containers
    docker-compose up -d
    
    # Wait for application to be ready
    print_info "Waiting for application to start..."
    sleep 10
    
    # Check if container is running
    if docker-compose ps | grep -q "Up"; then
        print_success "Application started successfully"
    else
        print_error "Failed to start application"
        docker-compose logs
        exit 1
    fi
}

# Create systemd service
create_systemd_service() {
    print_info "Creating systemd service..."
    
    SERVICE_FILE="/etc/systemd/system/email-validator-pro.service"
    
    cat > "$SERVICE_FILE" << EOF
[Unit]
Description=Email Validator Pro Service
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/email-validator-pro
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
ExecReload=/usr/local/bin/docker-compose restart
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable email-validator-pro.service
    
    print_success "Systemd service created and enabled"
}

# Display deployment info
show_deployment_info() {
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║          Deployment Completed Successfully!             ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    # Get server IP
    SERVER_IP=$(hostname -I | awk '{print $1}')
    
    print_info "Access Information:"
    echo ""
    echo -e "  🌐 Web Dashboard:    http://${SERVER_IP}:5000"
    echo -e "  📡 Realtime UI:      http://${SERVER_IP}:5000/static/realtime_validator.html"
    echo -e "  🔍 API Health:       http://${SERVER_IP}:5000/api/health"
    echo -e "  📊 API Stats:        http://${SERVER_IP}:5000/api/db/stats"
    echo ""
    
    print_info "Management Commands:"
    echo ""
    echo -e "  Start:    ${YELLOW}systemctl start email-validator-pro${NC}"
    echo -e "  Stop:     ${YELLOW}systemctl stop email-validator-pro${NC}"
    echo -e "  Restart:  ${YELLOW}systemctl restart email-validator-pro${NC}"
    echo -e "  Status:   ${YELLOW}systemctl status email-validator-pro${NC}"
    echo -e "  Logs:     ${YELLOW}docker-compose logs -f${NC}"
    echo ""
    
    print_info "Docker Commands:"
    echo ""
    echo -e "  View containers:  ${YELLOW}docker-compose ps${NC}"
    echo -e "  View logs:        ${YELLOW}docker-compose logs -f email-validator-pro${NC}"
    echo -e "  Rebuild:          ${YELLOW}docker-compose up -d --build${NC}"
    echo -e "  Stop all:         ${YELLOW}docker-compose down${NC}"
    echo ""
    
    print_success "Deployment completed!"
}

# Main deployment flow
main() {
    print_header
    
    print_info "Starting deployment process..."
    echo ""
    
    # Run deployment steps
    check_root
    check_ubuntu
    update_system
    install_docker
    install_docker_compose
    configure_firewall
    setup_application
    start_application
    create_systemd_service
    
    # Show completion info
    show_deployment_info
}

# Run main function
main

exit 0
