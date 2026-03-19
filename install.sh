#!/bin/bash

###############################################################################
# Email Bot v3.0 - Installation Script
# Automated setup for email marketing platform
###############################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

print_header() {
    clear
    echo -e "${CYAN}"
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║        📧 Email Bot v3.0 - Installation Script            ║"
    echo "║           Automated Setup & Configuration                 ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_step() {
    echo -e "${BLUE}▶ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check if running in Termux
check_termux() {
    if [[ -d "$PREFIX" ]]; then
        echo -e "${CYAN}Detected Termux environment${NC}"
        return 0
    fi
    return 1
}

# Install Python packages
install_python_packages() {
    print_step "Installing Python packages..."
    
    if command -v pip3 &> /dev/null; then
        pip3 install -r requirements.txt
    elif command -v pip &> /dev/null; then
        pip install -r requirements.txt
    else
        print_error "pip not found! Please install Python pip first."
        exit 1
    fi
    
    print_success "Python packages installed"
}

# Create directories
create_directories() {
    print_step "Creating directories..."
    
    mkdir -p "$SCRIPT_DIR/data/images"
    mkdir -p "$SCRIPT_DIR/logs"
    mkdir -p "$SCRIPT_DIR/templates"
    
    # Create .gitkeep files
    touch "$SCRIPT_DIR/data/.gitkeep"
    touch "$SCRIPT_DIR/logs/.gitkeep"
    
    print_success "Directories created"
}

# Setup .env file
setup_env() {
    print_step "Setting up configuration..."
    
    if [[ -f "$SCRIPT_DIR/.env" ]]; then
        print_warning ".env already exists"
        read -p "Overwrite? (y/N): " overwrite
        if [[ ! "$overwrite" =~ ^[Yy]$ ]]; then
            print_success "Keeping existing .env"
            return
        fi
    fi
    
    # Copy from example
    if [[ -f "$SCRIPT_DIR/.env.example" ]]; then
        cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/.env"
        print_success ".env created from template"
    else
        # Create basic .env
        cat > "$SCRIPT_DIR/.env" << 'EOF'
# Email Bot Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password
SENDER_NAME=Your Name
BATCH_SIZE=25
DELAY_MIN=1
DELAY_MAX=3
GEMINI_API_KEY=
TELEGRAM_BOT_TOKEN=
EOF
        print_success ".env created"
    fi
    
    echo ""
    echo -e "${YELLOW}═══════════════════════════════════════════════════════${NC}"
    echo -e "${WHITE}Configuration Required${NC}"
    echo -e "${YELLOW}═══════════════════════════════════════════════════════${NC}"
    echo ""
    echo "Edit .env with your credentials:"
    echo "  nano $SCRIPT_DIR/.env"
    echo ""
    echo "Required settings:"
    echo "  - SENDER_EMAIL (your Gmail)"
    echo "  - SENDER_PASSWORD (Gmail App Password)"
    echo ""
    echo "Get Gmail App Password:"
    echo "  https://myaccount.google.com/apppasswords"
    echo ""
}

# Create sample email list
create_sample_list() {
    print_step "Creating sample email list..."
    
    if [[ ! -f "$SCRIPT_DIR/data/email_list.txt" ]]; then
        cat > "$SCRIPT_DIR/data/email_list.txt" << 'EOF'
# Email List
# Add recipient emails here (one per line)
# recipient1@example.com
# recipient2@example.com
EOF
        print_success "Sample email list created"
    else
        print_success "Email list already exists"
    fi
}

# Set permissions
set_permissions() {
    print_step "Setting permissions..."
    
    chmod +x "$SCRIPT_DIR/email-bot.sh" 2>/dev/null || true
    chmod +x "$SCRIPT_DIR/install.sh" 2>/dev/null || true
    
    print_success "Permissions set"
}

# Show next steps
show_next_steps() {
    echo ""
    echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
    echo -e "${WHITE} Installation Complete! 🎉${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
    echo ""
    echo "Next steps:"
    echo ""
    echo "1. Configure your credentials:"
    echo -e "   ${CYAN}nano .env${NC}"
    echo ""
    echo "2. Add your Gmail App Password:"
    echo -e "   ${CYAN}https://myaccount.google.com/apppasswords${NC}"
    echo ""
    echo "3. Start the application:"
    echo -e "   ${CYAN}./email-bot.sh${NC}"
    echo ""
    echo "4. Or send a test email:"
    echo -e "   ${CYAN}python test_email.py${NC}"
    echo ""
    echo -e "${YELLOW}═══════════════════════════════════════════════════════${NC}"
    echo -e "${WHITE}Quick Reference${NC}"
    echo -e "${YELLOW}═══════════════════════════════════════════════════════${NC}"
    echo ""
    echo "Commands:"
    echo "  ./email-bot.sh          - Interactive menu"
    echo "  python test_email.py    - Send test email"
    echo "  python stats_dashboard.py - View statistics"
    echo ""
    echo "Documentation:"
    echo "  cat README.md           - Full documentation"
    echo "  cat QUICK_USAGE.md      - Quick reference"
    echo "  cat SETUP_GUIDE.md      - Setup guide"
    echo ""
}

# Main installation
main() {
    print_header
    
    echo -e "${WHITE}This script will install Email Bot v3.0${NC}"
    echo ""
    read -p "Continue? (Y/n): " confirm
    
    if [[ "$confirm" =~ ^[Nn]$ ]]; then
        echo "Installation cancelled"
        exit 0
    fi
    
    echo ""
    
    # Run installation steps
    create_directories
    install_python_packages
    setup_env
    create_sample_list
    set_permissions
    
    # Show completion message
    show_next_steps
}

# Run main
main "$@"
