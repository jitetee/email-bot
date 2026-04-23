#!/bin/bash
###############################################################################
# Email Bot Web Application Launcher v5.0
# Enhanced Edition - REAL EMAIL SENDING (not demo/fake)
###############################################################################

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PORT=${1:-8080}

echo -e "\033[0;36m"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║        📧 Email Bot Web Application v5.0                  ║"
echo "║     Enhanced Edition - REAL EMAIL SENDING                 ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "\033[0m"

echo ""
echo "🌐 Starting Web Application..."
echo ""
echo "📍 URL: http://localhost:$PORT"
echo "📱 Mobile-responsive design"
echo "🎨 Advanced template editor"
echo "📧 REAL SMTP email sending (NOT demo/fake)"
echo ""
echo "═══════════════════════════════════════════════════════════"
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
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "⚙️  Configuration: Edit .env file with your SMTP credentials"
echo "⚠️  Press Ctrl+C to stop"
echo ""

cd "$SCRIPT_DIR"

# Check if .env exists
if [[ ! -f ".env" ]]; then
    echo -e "\033[0;31mERROR: .env file not found!\033[0m"
    echo "Please run ./setup.bash first or create .env file"
    exit 1
fi

# Start the enhanced web application (error-free version with real email sending)
python3 web_app_enhanced.py "$PORT"
