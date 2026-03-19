#!/bin/bash

###############################################################################
# Email Bot - Enhanced Interactive CLI (v3.0)
# Full menu system with sub-menus, quick actions, and auto-start options
###############################################################################

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/.env"
DATA_DIR="$SCRIPT_DIR/data"
LOGS_DIR="$SCRIPT_DIR/logs"
TEMPLATES_DIR="$SCRIPT_DIR/templates"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
BOLD='\033[1m'
NC='\033[0m'

# Load environment
load_env() {
    if [[ -f "$ENV_FILE" ]]; then
        # Load variables from .env file
        set -a
        source "$ENV_FILE"
        set +a
    fi
}

###############################################################################
# Print Functions
###############################################################################

print_banner() {
    clear
    echo -e "${CYAN}"
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║           📧 Email Bot v3.0 - Enhanced CLI                ║"
    echo "║     Compliance • Smart Sending • Easy Management          ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_main_menu() {
    echo -e "${WHITE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BOLD}                    MAIN MENU                                ${NC}"
    echo -e "${WHITE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "  ${GREEN}[1]${NC} 📤 Send Emails"
    echo -e "  ${GREEN}[2]${NC} 🎨 Templates"
    echo -e "  ${GREEN}[3]${NC} 📊 Analytics & Reports"
    echo -e "  ${GREEN}[4]${NC} ⚙️  Settings & Configuration"
    echo -e "  ${GREEN}[5]${NC} 🛠️  Tools & Utilities"
    echo -e "  ${GREEN}[6]${NC} 🌐 Open Web GUI (http://localhost:8080)"
    echo -e "  ${GREEN}[7]${NC} 📖 Help & Documentation"
    echo -e "  ${GREEN}[0]${NC} Exit"
    echo -e "${WHITE}═══════════════════════════════════════════════════════════${NC}"
}

print_send_menu() {
    echo -e "${WHITE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BOLD}                    SEND EMAILS                              ${NC}"
    echo -e "${WHITE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "  ${GREEN}[1]${NC} Send Single Email"
    echo -e "  ${GREEN}[2]${NC} Send Bulk Campaign"
    echo -e "  ${GREEN}[3]${NC} Send Test Email"
    echo -e "  ${GREEN}[4]${NC} Schedule Campaign"
    echo -e "  ${GREEN}[5]${NC} Warm-up Mode (New Accounts)"
    echo -e "  ${GREEN}[0]${NC} Back"
    echo -e "${WHITE}═══════════════════════════════════════════════════════════${NC}"
}

print_template_menu() {
    echo -e "${WHITE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BOLD}                 TEMPLATES                                   ${NC}"
    echo -e "${WHITE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "  ${GREEN}[1]${NC} Browse Templates by Category"
    echo -e "  ${GREEN}[2]${NC} View All Templates"
    echo -e "  ${GREEN}[3]${NC} Edit Template"
    echo -e "  ${GREEN}[4]${NC} Preview Template"
    echo -e "  ${GREEN}[5]${NC} Template Categories"
    echo -e "  ${GREEN}[0]${NC} Back"
    echo -e "${WHITE}═══════════════════════════════════════════════════════════${NC}"
}

print_analytics_menu() {
    echo -e "${WHITE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BOLD}                 ANALYTICS & REPORTS                         ${NC}"
    echo -e "${WHITE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "  ${GREEN}[1]${NC} Statistics Dashboard"
    echo -e "  ${GREEN}[2]${NC} Campaign Logs"
    echo -e "  ${GREEN}[3]${NC} Engagement Tracker"
    echo -e "  ${GREEN}[4]${NC} Bounce Reports"
    echo -e "  ${GREEN}[5]${NC} Email List Stats"
    echo -e "  ${GREEN}[6]${NC} A/B Test Results"
    echo -e "  ${GREEN}[0]${NC} Back"
    echo -e "${WHITE}═══════════════════════════════════════════════════════════${NC}"
}

print_settings_menu() {
    echo -e "${WHITE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BOLD}                 SETTINGS & CONFIG                           ${NC}"
    echo -e "${WHITE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "  ${GREEN}[1]${NC} Configure Email Credentials"
    echo -e "  ${GREEN}[2]${NC} Configure Delay Settings"
    echo -e "  ${GREEN}[3]${NC} Manage SMTP Accounts"
    echo -e "  ${GREEN}[4]${NC} Domain Authentication (SPF/DKIM/DMARC)"
    echo -e "  ${GREEN}[5]${NC} Compliance Settings"
    echo -e "  ${GREEN}[6]${NC} Save Configuration"
    echo -e "  ${GREEN}[0]${NC} Back"
    echo -e "${WHITE}═══════════════════════════════════════════════════════════${NC}"
}

print_tools_menu() {
    echo -e "${WHITE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BOLD}                 TOOLS & UTILITIES                           ${NC}"
    echo -e "${WHITE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "  ${GREEN}[1]${NC} Email List Manager"
    echo -e "  ${GREEN}[2]${NC} ✏️ Quick Email Editor (Add/Delete)"
    echo -e "  ${GREEN}[3]${NC} Email Validator"
    echo -e "  ${GREEN}[4]${NC} Spam Score Checker"
    echo -e "  ${GREEN}[5]${NC} Double Opt-In Manager"
    echo -e "  ${GREEN}[6]${NC} Compliance Footer Generator"
    echo -e "  ${GREEN}[7]${NC} CSS Injector"
    echo -e "  ${GREEN}[8]${NC} Template Manager"
    echo -e "  ${GREEN}[9]${NC} 🌐 Web Dashboard"
    echo -e "  ${GREEN}[0]${NC} Back"
    echo -e "${WHITE}═══════════════════════════════════════════════════════════${NC}"
}

print_help_menu() {
    echo -e "${WHITE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BOLD}                 HELP & DOCUMENTATION                        ${NC}"
    echo -e "${WHITE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "  ${GREEN}[1]${NC} Quick Start Guide"
    echo -e "  ${GREEN}[2]${NC} Compliance Guide"
    echo -e "  ${GREEN}[3]${NC} Deliverability Best Practices"
    echo -e "  ${GREEN}[4]${NC} View README"
    echo -e "  ${GREEN}[5]${NC} Check System Status"
    echo -e "  ${GREEN}[0]${NC} Back"
    echo -e "${WHITE}═══════════════════════════════════════════════════════════${NC}"
}

###############################################################################
# Action Functions
###############################################################################

send_single_email() {
    echo -e "${BLUE}=== Send Single Email ===${NC}"
    
    # Use credentials from .env if available
    if [[ -n "$SENDER_EMAIL" && -n "$SENDER_PASSWORD" ]]; then
        echo -e "${GREEN}✓ Using saved credentials:${NC} $SENDER_EMAIL"
        sender_email="$SENDER_EMAIL"
        sender_password="$SENDER_PASSWORD"
        sender_name="${SENDER_NAME:-Ezra}"
        
        read -p "Use saved credentials? (Y/n): " use_saved
        if [[ "$use_saved" =~ ^[Nn]$ ]]; then
            read -p "Sender email: " sender_email
            read -sp "Sender password: " sender_password
            echo ""
            read -p "Sender name: " sender_name
        fi
    else
        read -p "Sender email: " sender_email
        read -sp "Sender password: " sender_password
        echo ""
        read -p "Sender name: " sender_name
    fi
    
    read -p "Recipient email: " recipient
    read -p "Template name: " template
    read -p "Subject: " subject

    echo -e "${YELLOW}Sending...${NC}"
    python3 "$SCRIPT_DIR/email_sender_cli.py" \
        --single \
        --to "$recipient" \
        --email "$sender_email" \
        --password "$sender_password" \
        --name "$sender_name" \
        --template "$template" \
        --subject "$subject"

    echo -e "${GREEN}✓ Done!${NC}"
    read -p "Press Enter to continue..."
}

send_bulk_email() {
    echo -e "${BLUE}=== Send Bulk Campaign ===${NC}"
    
    # Use credentials from .env if available
    if [[ -n "$SENDER_EMAIL" && -n "$SENDER_PASSWORD" ]]; then
        echo -e "${GREEN}✓ Using saved credentials:${NC} $SENDER_EMAIL"
        sender_email="$SENDER_EMAIL"
        sender_password="$SENDER_PASSWORD"
        sender_name="${SENDER_NAME:-Ezra}"
        
        read -p "Use saved credentials? (Y/n): " use_saved
        if [[ "$use_saved" =~ ^[Nn]$ ]]; then
            read -p "Sender email: " sender_email
            read -sp "Sender password: " sender_password
            echo ""
            read -p "Sender name: " sender_name
        fi
    else
        read -p "Sender email: " sender_email
        read -sp "Sender password: " sender_password
        echo ""
        read -p "Sender name: " sender_name
    fi
    
    read -p "Template name: " template
    read -p "Subject: " subject
    read -p "Batch size [25]: " batch_size
    batch_size=${batch_size:-25}
    read -p "Delay min [1]: " delay_min
    delay_min=${delay_min:-1}
    read -p "Delay max [3]: " delay_max
    delay_max=${delay_max:-3}

    echo -e "${YELLOW}Starting bulk send...${NC}"
    python3 "$SCRIPT_DIR/email_sender_cli.py" \
        --bulk \
        --email "$sender_email" \
        --password "$sender_password" \
        --name "$sender_name" \
        --template "$template" \
        --subject "$subject" \
        --batch-size "$batch_size" \
        --delay-min "$delay_min" \
        --delay-max "$delay_max"

    echo -e "${GREEN}✓ Campaign complete!${NC}"
    read -p "Press Enter to continue..."
}

show_template_categories() {
    echo -e "${BLUE}=== Template Categories ===${NC}"
    echo ""
    echo "Promotion: flash_sale, modern_promo, bold, vibrant, luxury"
    echo "Business: pro, tech, minimal, elegant, zen"
    echo "Personal: friendly, warm, playful, fresh, retro"
    echo "Dark Mode: dark"
    echo ""
    read -p "Press Enter to continue..."
}

start_api_server() {
    echo -e "${BLUE}=== Starting API Server ===${NC}"
    read -p "Port [8080]: " port
    port=${port:-8080}
    
    echo -e "${GREEN}Starting server on http://localhost:$port${NC}"
    echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
    
    cd "$SCRIPT_DIR"
    python3 api_server.py --port "$port"
}

start_telegram_bot() {
    echo -e "${BLUE}=== Starting Telegram Bot ===${NC}"
    
    if [[ -z "$TELEGRAM_BOT_TOKEN" ]]; then
        echo -e "${RED}TELEGRAM_BOT_TOKEN not set in .env${NC}"
        echo -e "${CYAN}Create bot with @BotFather on Telegram${NC}"
        read -p "Press Enter to continue..."
        return
    fi
    
    cd "$SCRIPT_DIR"
    python3 telegram_bot.py
}

run_stats_dashboard() {
    echo -e "${BLUE}=== Statistics Dashboard ===${NC}"
    python3 "$SCRIPT_DIR/stats_dashboard.py"
    read -p "Press Enter to continue..."
}

run_engagement_tracker() {
    echo -e "${BLUE}=== Engagement Tracker ===${NC}"
    echo -e "${WHITE}Choose action:${NC}"
    echo "  1) Subscriber stats  2) Segments  3) Inactive  4) Top engaged"
    read -p "Choice [1]: " choice
    
    case $choice in
        2) python3 "$SCRIPT_DIR/engagement_tracker.py" segment ;;
        3) python3 "$SCRIPT_DIR/engagement_tracker.py" inactive 90 ;;
        4) python3 "$SCRIPT_DIR/engagement_tracker.py" top 20 ;;
        *) 
            read -p "Email: " email
            python3 "$SCRIPT_DIR/engagement_tracker.py" stats "$email"
            ;;
    esac
    read -p "Press Enter to continue..."
}

run_domain_checker() {
    echo -e "${BLUE}=== Domain Authentication Check ===${NC}"
    read -p "Domain: " domain
    read -p "Email provider [gmail]: " provider
    provider=${provider:-gmail}
    
    python3 "$SCRIPT_DIR/domain_auth_checker.py" "$domain" "$provider"
    read -p "Press Enter to continue..."
}

run_spam_checker() {
    echo -e "${BLUE}=== Spam Score Checker ===${NC}"
    read -p "Template name: " template
    python3 "$SCRIPT_DIR/spam_checker.py" "$template"
    read -p "Press Enter to continue..."
}

run_email_list_manager() {
    echo -e "${BLUE}=== Email List Manager ===${NC}"
    echo -e "${WHITE}Choose action:${NC}"
    echo "  1) Stats  2) Add email  3) Clean  4) Dedup  5) Import  6) Export"
    read -p "Choice [1]: " choice
    
    case $choice in
        2) read -p "Email: " email; python3 "$SCRIPT_DIR/email_list_manager.py" add "$email" ;;
        3) python3 "$SCRIPT_DIR/email_list_manager.py" clean ;;
        4) python3 "$SCRIPT_DIR/email_list_manager.py" dedup ;;
        5) read -p "CSV file: " file; python3 "$SCRIPT_DIR/email_list_manager.py" import "$file" ;;
        6) read -p "Output file: " file; python3 "$SCRIPT_DIR/email_list_manager.py" export "$file" ;;
        *) python3 "$SCRIPT_DIR/email_list_manager.py" stats ;;
    esac
    read -p "Press Enter to continue..."
}

run_opt_in_manager() {
    echo -e "${BLUE}=== Double Opt-In Manager ===${NC}"
    echo -e "${WHITE}Choose action:${NC}"
    echo "  1) Subscribe  2) Confirm  3) Unsubscribe  4) Check  5) Stats"
    read -p "Choice [5]: " choice
    
    case $choice in
        1) 
            read -p "Email: " email
            python3 "$SCRIPT_DIR/opt_in_manager.py" subscribe "$email"
            ;;
        2)
            read -p "Token: " token
            python3 "$SCRIPT_DIR/opt_in_manager.py" confirm "$token"
            ;;
        3)
            read -p "Email: " email
            python3 "$SCRIPT_DIR/opt_in_manager.py" unsubscribe "$email"
            ;;
        4)
            read -p "Email: " email
            python3 "$SCRIPT_DIR/opt_in_manager.py" check "$email"
            ;;
        *)
            python3 "$SCRIPT_DIR/opt_in_manager.py" stats
            ;;
    esac
    read -p "Press Enter to continue..."
}

show_quick_start() {
    echo -e "${BLUE}=== Quick Start Guide ===${NC}"
    echo ""
    echo -e "${WHITE}Step 1: Configure Email${NC}"
    echo "  - Go to Settings > Configure Email Credentials"
    echo "  - Use Gmail App Password (not regular password)"
    echo ""
    echo -e "${WHITE}Step 2: Add Recipients${NC}"
    echo "  - Go to Tools > Email List Manager"
    echo "  - Add emails or import from CSV"
    echo ""
    echo -e "${WHITE}Step 3: Create/Select Template${NC}"
    echo "  - Go to Templates > AI Template Generator"
    echo "  - Or browse existing templates"
    echo ""
    echo -e "${WHITE}Step 4: Send!${NC}"
    echo "  - Go to Send Emails > Send Bulk Campaign"
    echo ""
    echo -e "${YELLOW}Pro tip: Start the API server for web access!${NC}"
    echo ""
    read -p "Press Enter to continue..."
}

show_compliance_guide() {
    if [[ -f "$SCRIPT_DIR/COMPLIANCE_QUICKSTART.md" ]]; then
        echo -e "${BLUE}=== Compliance Quick Start ===${NC}"
        head -80 "$SCRIPT_DIR/COMPLIANCE_QUICKSTART.md" | sed 's/^#/  /g' 's/^\*\*/  - /g'
    else
        echo -e "${YELLOW}Compliance guide not found${NC}"
    fi
    read -p "Press Enter to continue..."
}

show_deliverability_guide() {
    if [[ -f "$SCRIPT_DIR/DELIVERABILITY_GUIDE.md" ]]; then
        echo -e "${BLUE}=== Deliverability Guide ===${NC}"
        echo "File: DELIVERABILITY_GUIDE.md"
        echo ""
        head -100 "$SCRIPT_DIR/DELIVERABILITY_GUIDE.md" | sed 's/^#/  /g' 's/^\*\*/  - /g'
    else
        echo -e "${YELLOW}Guide not found${NC}"
    fi
    read -p "Press Enter to continue..."
}

check_system_status() {
    echo -e "${BLUE}=== System Status ===${NC}"
    echo ""
    
    # Check Python
    if command -v python3 &> /dev/null; then
        echo -e "  ${GREEN}✓${NC} Python3: $(python3 --version)"
    else
        echo -e "  ${RED}✗${NC} Python3: Not installed"
    fi
    
    # Check dependencies
    echo -e "  ${GREEN}✓${NC} Checking modules..."
    for module in opt_in_manager engagement_tracker domain_auth_checker compliance_footer ai_template_generator; do
        if [[ -f "$SCRIPT_DIR/${module}.py" ]]; then
            echo -e "    ${GREEN}✓${NC} $module"
        else
            echo -e "    ${YELLOW}!${NC} $module (missing)"
        fi
    done
    
    # Check directories
    echo ""
    echo -e "  ${WHITE}Directories:${NC}"
    for dir in templates data logs; do
        if [[ -d "$SCRIPT_DIR/$dir" ]]; then
            echo -e "    ${GREEN}✓${NC} $dir"
        else
            echo -e "    ${RED}✗${NC} $dir (missing)"
        fi
    done
    
    # Check .env
    echo ""
    echo -e "  ${WHITE}Configuration:${NC}"
    if [[ -f "$ENV_FILE" ]]; then
        echo -e "    ${GREEN}✓${NC} .env file exists"
    else
        echo -e "    ${YELLOW}!${NC} .env file missing (copy from .env.example)"
    fi
    
    echo ""
    read -p "Press Enter to continue..."
}

###############################################################################
# Sub-Menu Handlers
###############################################################################

send_menu() {
    while true; do
        print_send_menu
        read -p "Choose option (0-5): " choice
        
        case $choice in
            1) send_single_email ;;
            2) send_bulk_email ;;
            3) python3 "$SCRIPT_DIR/send_test.py"; read -p "Press Enter..." ;;
            4) python3 "$SCRIPT_DIR/campaign_scheduler.py"; read -p "Press Enter..." ;;
            5) python3 "$SCRIPT_DIR/warmup_manager.py"; read -p "Press Enter..." ;;
            0) return ;;
            *) echo -e "${RED}Invalid option${NC}"; read -p "Press Enter..." ;;
        esac
    done
}

template_menu() {
    while true; do
        print_template_menu
        read -p "Choose option (0-5): " choice

        case $choice in
            1)
                # Browse by category
                echo -e "${GREEN}Categories:${NC}"
                echo "  1) Promotion  2) Business  3) Personal  4) Dark  5) Colorful  6) Elegant"
                read -p "Category: " cat
                python3 "$SCRIPT_DIR/template_preview.py"
                ;;
            2) python3 "$SCRIPT_DIR/template_preview.py" ;;
            3)
                read -p "Template name: " tmpl
                $EDITOR "$SCRIPT_DIR/templates/${tmpl}.html" 2>/dev/null || nano "$SCRIPT_DIR/templates/${tmpl}.html"
                ;;
            4)
                read -p "Template name: " tmpl
                python3 "$SCRIPT_DIR/template_preview.py" "$tmpl"
                ;;
            5) show_template_categories ;;
            0) return ;;
            *) echo -e "${RED}Invalid option${NC}"; read -p "Press Enter..." ;;
        esac
    done
}

analytics_menu() {
    while true; do
        print_analytics_menu
        read -p "Choose option (0-6): " choice
        
        case $choice in
            1) run_stats_dashboard ;;
            2)
                echo -e "${BLUE}=== Campaign Logs ===${NC}"
                ls -lt "$LOGS_DIR"/*.log 2>/dev/null | head -10
                ;;
            3) run_engagement_tracker ;;
            4) python3 "$SCRIPT_DIR/bounce_handler.py" stats; read -p "Press Enter..." ;;
            5) python3 "$SCRIPT_DIR/email_list_manager.py" stats; read -p "Press Enter..." ;;
            6) python3 "$SCRIPT_DIR/ab_test_manager.py" list; read -p "Press Enter..." ;;
            0) return ;;
            *) echo -e "${RED}Invalid option${NC}"; read -p "Press Enter..." ;;
        esac
    done
}

settings_menu_handler() {
    while true; do
        print_settings_menu
        read -p "Choose option (0-6): " choice

        case $choice in
            1)
                echo -e "${BLUE}=== Email Credentials ===${NC}"
                echo -e "${CYAN}Current settings from .env:${NC}"
                echo -e "  Email: ${GREEN}${SENDER_EMAIL:-<not set>}${NC}"
                echo -e "  Name:  ${GREEN}${SENDER_NAME:-<not set>}${NC}"
                echo -e "  SMTP:  ${GREEN}${SMTP_SERVER:-smtp.gmail.com}:${SMTP_PORT:-587}${NC}"
                echo ""
                echo -e "${YELLOW}Press Enter to keep current value${NC}"
                read -p "Email [$SENDER_EMAIL]: " input_email
                [[ -n "$input_email" ]] && SENDER_EMAIL="$input_email"
                read -sp "Password [$SENDER_PASSWORD]: " input_password
                echo ""
                [[ -n "$input_password" ]] && SENDER_PASSWORD="$input_password"
                read -p "Sender Name [$SENDER_NAME]: " input_name
                [[ -n "$input_name" ]] && SENDER_NAME="$input_name"
                echo -e "${GREEN}✓ Credentials updated (not saved yet)${NC}"
                ;;
            2)
                echo -e "${BLUE}=== Delay Settings ===${NC}"
                echo -e "${CYAN}Current settings from .env:${NC}"
                echo -e "  Delay Min: ${GREEN}${DELAY_MIN:-1}s${NC}"
                echo -e "  Delay Max: ${GREEN}${DELAY_MAX:-3}s${NC}"
                echo -e "  Batch Size:${GREEN} ${BATCH_SIZE:-25}${NC}"
                echo ""
                echo -e "${YELLOW}Press Enter to keep current value${NC}"
                read -p "Delay Min [$DELAY_MIN]: " input_min
                [[ -n "$input_min" ]] && DELAY_MIN="$input_min"
                read -p "Delay Max [$DELAY_MAX]: " input_max
                [[ -n "$input_max" ]] && DELAY_MAX="$input_max"
                read -p "Batch Size [$BATCH_SIZE]: " input_batch
                [[ -n "$input_batch" ]] && BATCH_SIZE="$input_batch"
                echo -e "${GREEN}✓ Delay settings updated (not saved yet)${NC}"
                ;;
            3) python3 "$SCRIPT_DIR/smtp_account_manager.py" list; read -p "Press Enter..." ;;
            4) run_domain_checker ;;
            5) python3 "$SCRIPT_DIR/compliance_footer.py"; read -p "Press Enter..." ;;
            6)
                cat > "$ENV_FILE" << EOF
# Email Bot Configuration
SMTP_SERVER=${SMTP_SERVER:-smtp.gmail.com}
SMTP_PORT=${SMTP_PORT:-587}
SENDER_EMAIL=$SENDER_EMAIL
SENDER_PASSWORD=$SENDER_PASSWORD
SENDER_NAME=$SENDER_NAME
DELAY_MIN=${DELAY_MIN:-1}
DELAY_MAX=${DELAY_MAX:-3}
BATCH_SIZE=${BATCH_SIZE:-25}
DELAY_BETWEEN_BATCHES=${DELAY_BETWEEN_BATCHES:-30}
GEMINI_API_KEY=${GEMINI_API_KEY:-}
TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN:-}
EOF
                echo -e "${GREEN}✓ Settings saved to .env!${NC}"
                echo -e "${YELLOW}Reload to apply: source .env${NC}"
                ;;
            0) return ;;
            *) echo -e "${RED}Invalid option${NC}"; read -p "Press Enter..." ;;
        esac
    done
}

tools_menu() {
    while true; do
        print_tools_menu
        read -p "Choose option (0-9): " choice

        case $choice in
            1) run_email_list_manager ;;
            2)
                # Quick Email Editor
                echo -e "${BLUE}=== Quick Email Editor ===${NC}"
                echo -e "${WHITE}Choose action:${NC}"
                echo "  1) List emails     2) Add emails     3) Delete by number"
                read -p "Choice [1]: " editor_choice
                case $editor_choice in
                    2) python3 "$SCRIPT_DIR/email_list_editor.py" add ;;
                    3)
                        read -p "Enter line numbers to delete (e.g., 5 or 1,3,7): " nums
                        python3 "$SCRIPT_DIR/email_list_editor.py" delete "$nums"
                        ;;
                    *) python3 "$SCRIPT_DIR/email_list_editor.py" list ;;
                esac
                read -p "Press Enter..."
                ;;
            3)
                read -p "Email: " email
                python3 "$SCRIPT_DIR/email_validator.py" "$email"
                read -p "Press Enter..."
                ;;
            4) run_spam_checker ;;
            5) run_opt_in_manager ;;
            6) python3 "$SCRIPT_DIR/compliance_footer.py"; read -p "Press Enter..." ;;
            7) python3 "$SCRIPT_DIR/css_injector.py" presets; read -p "Press Enter..." ;;
            8) python3 "$SCRIPT_DIR/template_manager.py" list; read -p "Press Enter..." ;;
            9)
                echo -e "${BLUE}=== Starting Web Dashboard ===${NC}"
                echo -e "${GREEN}Opening http://localhost:8000${NC}"
                echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
                cd "$SCRIPT_DIR"
                python3 web_dashboard.py 8000
                ;;
            0) return ;;
            *) echo -e "${RED}Invalid option${NC}"; read -p "Press Enter..." ;;
        esac
    done
}

help_menu() {
    while true; do
        print_help_menu
        read -p "Choose option (0-5): " choice
        
        case $choice in
            1) show_quick_start ;;
            2) show_compliance_guide ;;
            3) show_deliverability_guide ;;
            4)
                if command -v less &> /dev/null; then
                    less "$SCRIPT_DIR/README.md"
                else
                    head -100 "$SCRIPT_DIR/README.md"
                fi
                ;;
            5) check_system_status ;;
            0) return ;;
            *) echo -e "${RED}Invalid option${NC}"; read -p "Press Enter..." ;;
        esac
    done
}

###############################################################################
# Auto-Start Functions
###############################################################################

auto_start_server() {
    echo -e "${CYAN}=== Auto-Starting API Server ===${NC}"
    
    # Check if port is available
    if command -v netstat &> /dev/null; then
        if netstat -tuln | grep -q ":8080"; then
            echo -e "${YELLOW}Port 8080 is already in use${NC}"
            return 1
        fi
    fi
    
    # Start server in background
    echo -e "${GREEN}Starting API server on http://localhost:8080${NC}"
    cd "$SCRIPT_DIR"
    nohup python3 api_server.py --port 8080 > logs/api_server.log 2>&1 &
    echo -e "${GREEN}✓ Server started!${NC}"
    echo -e "${CYAN}Logs: logs/api_server.log${NC}"
    echo -e "${YELLOW}Stop with: kill \$(pgrep -f 'api_server.py')${NC}"
}

auto_start_menu() {
    echo -e "${WHITE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BOLD}                 AUTO-START OPTIONS                          ${NC}"
    echo -e "${WHITE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "  ${GREEN}[1]${NC} Start API Server (port 8080)"
    echo -e "  ${GREEN}[2]${NC} Start Telegram Bot"
    echo -e "  ${GREEN}[3]${NC} Start Both"
    echo -e "  ${GREEN}[0]${NC} Skip (go to main menu)"
    echo -e "${WHITE}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    read -p "Auto-start option (0-3): " auto_choice
    
    case $auto_choice in
        1) auto_start_server ;;
        2)
            echo -e "${BLUE}Starting Telegram Bot...${NC}"
            cd "$SCRIPT_DIR"
            nohup python3 telegram_bot.py > logs/telegram_bot.log 2>&1 &
            echo -e "${GREEN}✓ Telegram bot started!${NC}"
            ;;
        3)
            auto_start_server
            sleep 1
            echo -e "${BLUE}Starting Telegram Bot...${NC}"
            cd "$SCRIPT_DIR"
            nohup python3 telegram_bot.py > logs/telegram_bot.log 2>&1 &
            echo -e "${GREEN}✓ Both services started!${NC}"
            ;;
    esac
}

###############################################################################
# Main Script
###############################################################################

main() {
    load_env

    # Check for web GUI start
    if [[ "$1" == "--web" || "$1" == "-w" ]]; then
        python3 "$SCRIPT_DIR/web_gui.py" 8080
        exit 0
    fi

    print_banner

    # Main loop
    while true; do
        print_main_menu
        read -p "Choose option (0-7): " choice

        case $choice in
            1) send_menu ;;
            2) template_menu ;;
            3) analytics_menu ;;
            4) settings_menu_handler ;;
            5) tools_menu ;;
            6)
                echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
                echo -e "${BLUE}║          🌐 Starting Web GUI Server                        ║${NC}"
                echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
                echo ""
                echo -e "${GREEN}✓ Web GUI starting at: http://localhost:8080${NC}"
                echo -e "${GREEN}✓ Also available at: http://127.0.0.1:8080${NC}"
                echo ""
                echo -e "${WHITE}Features:${NC}"
                echo -e "  📝 Visual email composer"
                echo -e "  🎨 Template browser"
                echo -e "  📋 Email list manager"
                echo -e "  📊 Analytics dashboard"
                echo -e "  ⚙️  Settings panel"
                echo ""
                echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
                echo ""
                cd "$SCRIPT_DIR"
                python3 web_gui.py 8080
                ;;
            7) help_menu ;;
            0)
                echo -e "${GREEN}Goodbye!${NC}"
                exit 0
                ;;
            *)
                echo -e "${RED}Invalid option${NC}"
                read -p "Press Enter to continue..."
                ;;
        esac
    done
}

# Run main
main "$@"
