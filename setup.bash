#!/bin/bash

###############################################################################
# Email Bot v5.0 - Complete Setup Script
# Automated installation for email marketing platform with web interface
###############################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

###############################################################################
# Helper Functions
###############################################################################

print_header() {
    clear
    echo -e "${CYAN}"
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║        📧 Email Bot v5.0 - Setup Script                   ║"
    echo "║     Complete Email Marketing Platform with Web UI         ║"
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

check_termux() {
    if [[ -d "$PREFIX" ]]; then
        echo -e "${CYAN}Detected Termux environment${NC}"
        return 0
    fi
    return 1
}

###############################################################################
# Installation Steps
###############################################################################

# Check Python installation
check_python() {
    print_step "Checking Python installation..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
        PYTHON_VERSION=$(python3 --version)
        print_success "Python found: $PYTHON_VERSION"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
        PYTHON_VERSION=$(python --version)
        print_success "Python found: $PYTHON_VERSION"
    else
        print_error "Python not found! Please install Python 3.8+ first."
        echo ""
        echo "Install Python:"
        echo "  - Ubuntu/Debian: sudo apt install python3 python3-pip"
        echo "  - Termux: pkg install python"
        echo "  - macOS: brew install python"
        exit 1
    fi
}

# Check pip installation
check_pip() {
    print_step "Checking pip installation..."
    
    if command -v pip3 &> /dev/null; then
        PIP_CMD="pip3"
    elif command -v pip &> /dev/null; then
        PIP_CMD="pip"
    else
        print_error "pip not found! Please install Python pip first."
        echo ""
        echo "Install pip:"
        echo "  - Ubuntu/Debian: sudo apt install python3-pip"
        echo "  - Termux: pkg install python-pip"
        exit 1
    fi
    
    print_success "pip found: $($PIP_CMD --version)"
}

# Install Python packages
install_packages() {
    print_step "Installing Python packages..."
    echo ""
    
    if [[ -f "$SCRIPT_DIR/requirements.txt" ]]; then
        $PIP_CMD install -r requirements.txt --upgrade
        print_success "Python packages installed"
    else
        # Install basic packages if requirements.txt missing
        $PIP_CMD install flask python-dotenv dnspython aiohttp
        print_success "Basic Python packages installed"
    fi
}

# Create required directories
create_directories() {
    print_step "Creating directories..."
    
    mkdir -p "$SCRIPT_DIR/data/images"
    mkdir -p "$SCRIPT_DIR/logs"
    mkdir -p "$SCRIPT_DIR/templates"
    mkdir -p "$SCRIPT_DIR/data/segments"
    
    # Create .gitkeep files
    touch "$SCRIPT_DIR/data/.gitkeep"
    touch "$SCRIPT_DIR/logs/.gitkeep"
    touch "$SCRIPT_DIR/templates/.gitkeep"
    
    print_success "Directories created"
}

# Setup .env configuration file
setup_env() {
    print_step "Setting up configuration file..."
    
    if [[ -f "$SCRIPT_DIR/.env" ]]; then
        print_warning ".env already exists"
        echo ""
        read -p "Overwrite existing configuration? (y/N): " overwrite
        if [[ ! "$overwrite" =~ ^[Yy]$ ]]; then
            print_success "Keeping existing .env configuration"
            return
        fi
    fi
    
    # Copy from example if available
    if [[ -f "$SCRIPT_DIR/.env.example" ]]; then
        cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/.env"
        print_success ".env created from template"
    else
        # Create basic .env
        cat > "$SCRIPT_DIR/.env" << 'EOF'
# Email Bot Configuration
# Copy this to .env and fill in your values

# =============================================================================
# SMTP Email Settings (Gmail App Password Recommended)
# =============================================================================
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password_here
SENDER_NAME=Your Company

# =============================================================================
# Bulk Email Settings - Anti-Spam Configuration
# =============================================================================
BATCH_SIZE=25
DELAY_BETWEEN_BATCHES=30
DELAY_MIN=1.0
DELAY_MAX=3.0
DELAY_BETWEEN_EMAILS=1.0

# =============================================================================
# Telegram Bot Token (optional - for notifications)
# =============================================================================
TELEGRAM_BOT_TOKEN=your_bot_token_here

# =============================================================================
# AI Template Generation (optional)
# =============================================================================
GEMINI_API_KEY=your_gemini_api_key_here
EOF
        print_success ".env created"
    fi
    
    echo ""
    echo -e "${YELLOW}═══════════════════════════════════════════════════════${NC}"
    echo -e "${WHITE}Configuration Required${NC}"
    echo -e "${YELLOW}═══════════════════════════════════════════════════════${NC}"
    echo ""
    echo "Edit .env with your SMTP credentials:"
    echo -e "  ${CYAN}nano $SCRIPT_DIR/.env${NC}"
    echo ""
    echo "Required settings:"
    echo "  - SENDER_EMAIL (your Gmail address)"
    echo "  - SENDER_PASSWORD (Gmail App Password)"
    echo ""
    echo "Get Gmail App Password:"
    echo -e "  ${CYAN}https://myaccount.google.com/apppasswords${NC}"
    echo ""
}

# Create sample email list
create_sample_list() {
    print_step "Creating sample email list..."
    
    if [[ ! -f "$SCRIPT_DIR/data/email_list.txt" ]]; then
        cat > "$SCRIPT_DIR/data/email_list.txt" << 'EOF'
# Email List
# Add recipient emails here (one per line)
# Format: email@example.com
# Lines starting with # are comments

# Add your test emails below:
# test1@example.com
# test2@example.com
EOF
        print_success "Sample email list created"
    else
        print_success "Email list already exists"
    fi
}

# Create sample template
create_sample_template() {
    print_step "Creating sample email template..."
    
    if [[ ! -f "$SCRIPT_DIR/templates/welcome.html" ]]; then
        cat > "$SCRIPT_DIR/templates/welcome.html" << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Welcome!</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h1 style="color: #667eea;">Welcome!</h1>
        <p>Hi there,</p>
        <p>Thank you for joining us! We're excited to have you on board.</p>
        <p>Best regards,<br>Your Team</p>
        <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
        <p style="font-size: 12px; color: #888;">
            © 2024 Your Company. All rights reserved.
        </p>
    </div>
</body>
</html>
EOF
        print_success "Sample template created"
    else
        print_success "Sample template already exists"
    fi
}

# Set script permissions
set_permissions() {
    print_step "Setting permissions..."
    
    chmod +x "$SCRIPT_DIR/email-bot.sh" 2>/dev/null || true
    chmod +x "$SCRIPT_DIR/install.sh" 2>/dev/null || true
    chmod +x "$SCRIPT_DIR/start_web_app.sh" 2>/dev/null || true
    chmod +x "$SCRIPT_DIR/setup.bash" 2>/dev/null || true
    
    print_success "Permissions set"
}

###############################################################################
# Web Application Launcher
###############################################################################

create_web_launcher() {
    print_step "Creating web application launcher..."
    
    cat > "$SCRIPT_DIR/start_web.sh" << 'EOF'
#!/bin/bash
###############################################################################
# Email Bot Web Application Launcher v5.0
# Starts the enhanced web interface with REAL email sending
###############################################################################

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PORT=${1:-8080}

echo -e "\033[0;36m"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║        📧 Email Bot Web Application v5.0                  ║"
echo "║     Enhanced Edition - REAL EMAIL SENDING                ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "\033[0m"

echo ""
echo "🌐 Starting Web Application..."
echo ""
echo "📍 URL: http://localhost:$PORT"
echo "📱 Mobile-responsive design"
echo "🎨 Advanced template editor"
echo "📧 REAL SMTP email sending (not demo/fake)"
echo ""
echo "Features:"
echo "  ✓ Dashboard with real-time statistics"
echo "  ✓ Send single/bulk emails via REAL SMTP"
echo "  ✓ Schedule campaigns"
echo "  ✓ SMTP warm-up mode"
echo "  ✓ Template management (browse, create, edit, preview)"
echo "  ✓ Email list management (add, validate, clean, import/export)"
echo "  ✓ Analytics & reporting"
echo "  ✓ A/B testing"
echo "  ✓ SMTP account management"
echo "  ✓ Domain authentication check"
echo "  ✓ Spam score checker"
echo "  ✓ Double opt-in manager"
echo "  ✓ Compliance footer generator"
echo "  ✓ CSS injector"
echo "  ✓ Email signature creator"
echo "  ✓ Signup form generator"
echo "  ✓ Preheader generator"
echo "  ✓ Image management"
echo "  ✓ Link tracking"
echo ""
echo "⚙️  Configuration: Edit .env file with your SMTP credentials"
echo "⚠️  Press Ctrl+C to stop"
echo "═══════════════════════════════════════════════════════════"
echo ""

cd "$SCRIPT_DIR"

# Check if .env exists
if [[ ! -f ".env" ]]; then
    echo -e "\033[0;31mERROR: .env file not found!\033[0m"
    echo "Please run ./setup.bash first or create .env file"
    exit 1
fi

# Start the enhanced web application
python3 web_app_enhanced.py "$PORT"
EOF

    chmod +x "$SCRIPT_DIR/start_web.sh"
    print_success "Web launcher created: start_web.sh"
}

###############################################################################
# Quick Start Guide
###############################################################################

show_next_steps() {
    echo ""
    echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
    echo -e "${WHITE} Setup Complete! 🎉${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
    echo ""
    echo "Next steps:"
    echo ""
    echo "1. Configure your SMTP credentials:"
    echo -e "   ${CYAN}nano .env${NC}"
    echo ""
    echo "2. Get Gmail App Password (required):"
    echo -e "   ${CYAN}https://myaccount.google.com/apppasswords${NC}"
    echo ""
    echo "3. Start the Web Application (RECOMMENDED):"
    echo -e "   ${CYAN}./start_web.sh${NC}"
    echo ""
    echo "   Or start the classic web app:"
    echo -e "   ${CYAN}./start_web_app.sh${NC}"
    echo ""
    echo "4. Or use the interactive CLI:"
    echo -e "   ${CYAN}./email-bot.sh${NC}"
    echo ""
    echo -e "${YELLOW}═══════════════════════════════════════════════════════${NC}"
    echo -e "${WHITE}Quick Reference${NC}"
    echo -e "${YELLOW}═══════════════════════════════════════════════════════${NC}"
    echo ""
    echo "Commands:"
    echo "  ./start_web.sh          - Start enhanced web UI (RECOMMENDED)"
    echo "  ./start_web_app.sh      - Start classic web UI"
    echo "  ./email-bot.sh          - Interactive CLI menu"
    echo "  python3 api_server.py   - Start REST API server"
    echo ""
    echo "Important Files:"
    echo "  .env                    - Configuration (SMTP credentials)"
    echo "  data/email_list.txt     - Email recipient list"
    echo "  templates/              - Email templates"
    echo "  logs/                   - Campaign logs"
    echo ""
    echo "Documentation:"
    echo "  cat README.md           - Full documentation"
    echo "  cat SETUP_GUIDE.md      - Detailed setup guide"
    echo "  cat QUICK_USAGE.md      - Quick reference"
    echo ""
    echo -e "${YELLOW}═══════════════════════════════════════════════════════${NC}"
    echo -e "${WHITE}Important Notes${NC}"
    echo -e "${YELLOW}═══════════════════════════════════════════════════════${NC}"
    echo ""
    echo "⚠️  Gmail Users: You MUST use an App Password, not your regular"
    echo "    password. See: https://support.google.com/accounts/answer/185833"
    echo ""
    echo "⚠️  Bulk Sending: Start with small batches (10-25 emails) and"
    echo "    gradually increase to avoid spam filters."
    echo ""
    echo "⚠️  Warm-up: Use SMTP warm-up mode for new email accounts to"
    echo "    build sender reputation before large campaigns."
    echo ""
}

###############################################################################
# Main Installation
###############################################################################

main() {
    print_header
    
    echo -e "${WHITE}This script will install Email Bot v5.0${NC}"
    echo ""
    echo "Components to install:"
    echo "  ✓ Python dependencies (Flask, aiohttp, etc.)"
    echo "  ✓ Directory structure (data, logs, templates)"
    echo "  ✓ Configuration file (.env)"
    echo "  ✓ Sample email list and templates"
    echo "  ✓ Web application launcher"
    echo ""
    read -p "Continue with installation? (Y/n): " confirm
    
    if [[ "$confirm" =~ ^[Nn]$ ]]; then
        echo "Installation cancelled"
        exit 0
    fi
    
    echo ""
    
    # Run installation steps
    check_python
    check_pip
    install_packages
    create_directories
    setup_env
    create_sample_list
    create_sample_template
    set_permissions
    create_web_launcher
    
    # Show completion message
    show_next_steps
}

# Run main function
main "$@"
