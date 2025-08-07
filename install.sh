#!/bin/bash

# Wonder Discord Bot - Automated Installation Script
# For VPS and Linux servers

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="/opt/wonder-discord-bot"
SERVICE_NAME="wonder-bot"
PYTHON_VERSION="3.8"

print_header() {
    echo -e "${BLUE}"
    echo "=============================================="
    echo "  Wonder Discord Bot - Automated Installer"
    echo "=============================================="
    echo -e "${NC}"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

check_os() {
    print_step "Checking operating system..."
    
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        OS=$NAME
        print_success "Detected OS: $OS"
    else
        print_error "Cannot determine operating system"
        exit 1
    fi
}

install_dependencies() {
    print_step "Installing system dependencies..."
    
    # Update package list
    apt update -y
    
    # Install Python and pip
    apt install -y python3 python3-pip python3-venv python3-dev
    
    # Install system libraries for Pillow
    apt install -y libjpeg-dev zlib1g-dev libfreetype6-dev liblcms2-dev libopenjp2-7-dev libtiff5-dev
    
    # Install git and other utilities
    apt install -y git curl wget unzip
    
    print_success "System dependencies installed"
}

create_user() {
    print_step "Creating bot user..."
    
    if ! id "botuser" &>/dev/null; then
        useradd -r -s /bin/false -d $INSTALL_DIR botuser
        print_success "Created user: botuser"
    else
        print_warning "User 'botuser' already exists"
    fi
}

setup_directories() {
    print_step "Setting up directories..."
    
    # Create installation directory
    mkdir -p $INSTALL_DIR
    
    # Set ownership
    chown -R botuser:botuser $INSTALL_DIR
    chmod 755 $INSTALL_DIR
    
    print_success "Directories created"
}

install_bot() {
    print_step "Installing bot files..."
    
    # Check if we're already in the bot directory
    if [[ -f "run.py" && -f "requirements.txt" ]]; then
        print_success "Bot files found in current directory"
        
        # Copy files to installation directory
        cp -r . $INSTALL_DIR/
        
        # Remove installation files from target
        rm -f $INSTALL_DIR/install.sh
        rm -f $INSTALL_DIR/wonder-bot.service
        
    else
        print_error "Bot files not found. Please run this script from the bot directory."
        exit 1
    fi
    
    # Set correct ownership
    chown -R botuser:botuser $INSTALL_DIR
    
    print_success "Bot files installed"
}

install_python_dependencies() {
    print_step "Installing Python dependencies..."
    
    cd $INSTALL_DIR
    
    # Install dependencies as botuser
    sudo -u botuser python3 -m pip install --user -r requirements.txt
    
    print_success "Python dependencies installed"
}

configure_environment() {
    print_step "Configuring environment..."
    
    # Check if .env exists
    if [[ ! -f "$INSTALL_DIR/.env" ]]; then
        print_warning ".env file not found, creating template"
        
        cat > $INSTALL_DIR/.env << 'EOF'
# Discord Bot Configuration
# REQUIRED: Replace with your actual Discord bot token
DISCORD_TOKEN=YOUR_DISCORD_BOT_TOKEN_HERE

# Optional: Premium and Booster role IDs
PREMIUM_ROLE_ID=YOUR_PREMIUM_ROLE_ID_HERE
BOOSTER_ROLE_ID=YOUR_BOOSTER_ROLE_ID_HERE

# Database Configuration (Optional - SQLite used by default)
# Uncomment and configure for MySQL
# DB_TYPE=mysql
# DB_HOST=localhost
# DB_PORT=3306
# DB_NAME=wonder_bot
# DB_USER=your_username
# DB_PASSWORD=your_password
EOF
        
        chown botuser:botuser $INSTALL_DIR/.env
        chmod 600 $INSTALL_DIR/.env
        
        print_warning "Please edit $INSTALL_DIR/.env and set your Discord token"
    else
        print_success ".env file already exists"
    fi
}

install_service() {
    print_step "Installing systemd service..."
    
    # Create service file
    cat > /etc/systemd/system/$SERVICE_NAME.service << EOF
[Unit]
Description=Wonder Discord Bot
After=network.target
Wants=network.target

[Service]
Type=simple
User=botuser
Group=botuser
WorkingDirectory=$INSTALL_DIR
ExecStart=/usr/bin/python3 $INSTALL_DIR/run.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier=wonder-bot

# Environment variables
Environment=PYTHONPATH=$INSTALL_DIR/src
EnvironmentFile=-$INSTALL_DIR/.env

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$INSTALL_DIR

[Install]
WantedBy=multi-user.target
EOF
    
    # Reload systemd and enable service
    systemctl daemon-reload
    systemctl enable $SERVICE_NAME
    
    print_success "Systemd service installed and enabled"
}

setup_firewall() {
    print_step "Configuring firewall..."
    
    # Check if ufw is available
    if command -v ufw &> /dev/null; then
        # Enable basic firewall rules
        ufw --force enable
        ufw allow ssh
        ufw allow 80/tcp
        ufw allow 443/tcp
        
        print_success "Basic firewall rules configured"
    else
        print_warning "UFW not found, skipping firewall configuration"
    fi
}

create_logrotate() {
    print_step "Setting up log rotation..."
    
    cat > /etc/logrotate.d/wonder-bot << 'EOF'
/var/log/wonder-bot/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0644 botuser botuser
    postrotate
        systemctl reload wonder-bot
    endscript
}
EOF
    
    # Create log directory
    mkdir -p /var/log/wonder-bot
    chown botuser:botuser /var/log/wonder-bot
    
    print_success "Log rotation configured"
}

test_installation() {
    print_step "Testing installation..."
    
    cd $INSTALL_DIR
    
    # Test Python imports
    if sudo -u botuser python3 -c "import sys; sys.path.insert(0, 'src'); from main import WonderBot; print('✅ Bot imports successful')"; then
        print_success "Bot imports test passed"
    else
        print_error "Bot imports test failed"
        return 1
    fi
    
    # Test environment file
    if [[ -f ".env" ]]; then
        if grep -q "YOUR_DISCORD_BOT_TOKEN_HERE" .env; then
            print_warning "Discord token not configured"
        else
            print_success "Discord token appears to be configured"
        fi
    fi
    
    print_success "Installation tests completed"
}

main() {
    print_header
    
    # Check requirements
    check_root
    check_os
    
    # Installation steps
    install_dependencies
    create_user
    setup_directories
    install_bot
    install_python_dependencies
    configure_environment
    install_service
    setup_firewall
    create_logrotate
    test_installation
    
    # Final instructions
    echo
    print_success "Installation completed successfully!"
    echo
    echo -e "${YELLOW}Next steps:${NC}"
    echo "1. Edit the Discord token in: $INSTALL_DIR/.env"
    echo "2. Start the bot: systemctl start $SERVICE_NAME"
    echo "3. Check status: systemctl status $SERVICE_NAME"
    echo "4. View logs: journalctl -u $SERVICE_NAME -f"
    echo
    echo -e "${BLUE}Useful commands:${NC}"
    echo "• Start bot: systemctl start $SERVICE_NAME"
    echo "• Stop bot: systemctl stop $SERVICE_NAME"
    echo "• Restart bot: systemctl restart $SERVICE_NAME"
    echo "• View logs: journalctl -u $SERVICE_NAME -f"
    echo "• Edit config: nano $INSTALL_DIR/.env"
    echo
}

# Run main function
main "$@"