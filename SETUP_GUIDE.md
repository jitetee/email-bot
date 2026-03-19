# 🚀 Setup Guide - Email Bot v3.0

## Quick Setup (5 minutes)

### Step 1: Install Dependencies

```bash
# Install all Python packages
pip install -r requirements.txt

# Or install AI package separately if pip is slow:
pip install google-generativeai
```

### Step 2: Configure Environment

```bash
# Copy example config
cp .env.example .env

# Edit .env with your credentials
# Use nano, vim, or any text editor
nano .env
```

**Required settings:**
```env
# Email (Gmail App Password recommended)
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# AI Template Generation (optional)
GEMINI_API_KEY=your_gemini_api_key
```

### Step 3: Get API Keys

#### Gmail App Password
1. Go to Google Account: https://myaccount.google.com
2. Enable 2-Factor Authentication
3. Visit: https://myaccount.google.com/apppasswords
4. Select "Mail" and your device
5. Copy the 16-character password
6. Paste in `.env` as `SENDER_PASSWORD`

#### Google Gemini API Key (for AI templates)
1. Visit: https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the key
5. Paste in `.env` as `GEMINI_API_KEY`

### Step 4: Test Installation

```bash
# Check all modules work
python opt_in_manager.py stats
python engagement_tracker.py segment
python domain_auth_checker.py gmail.com

# Test AI template generator (if API key set)
python ai_template_generator.py "Test email"
```

### Step 5: Start Using

```bash
# Interactive menu
./email-bot.sh

# Or auto-start server
./email-bot.sh --auto
```

---

## 🔒 Security Setup

### .gitignore is Configured

The following are **automatically ignored** by git:

```
.env                    # All environment files
*.key                   # API keys
*.secret                # Secrets
data/*.json            # Generated data
logs/*.log             # Log files
templates/ai_*.html    # AI-generated templates
```

### ⚠️ NEVER Commit These Files

- `.env` - Contains passwords and API keys
- `data/email_list.txt` - Contains subscriber emails
- `logs/*.log` - May contain sensitive data
- Any `*.key` or `*.secret` files

### Verify Before Committing

```bash
# Always check before git add
git status

# Should NOT show .env or data files
# If you see them, DO NOT add them!
```

---

## 📦 Package Requirements

### Core Dependencies (Required)
```
python-telegram-bot==20.7    # Telegram bot
aiohttp>=3.8.0               # Async HTTP
dnspython>=2.3.0             # Email validation
```

### AI Dependencies (Optional - for AI templates)
```
google-generativeai>=0.3.0   # Google Gemini AI
```

### Install Individual Packages

```bash
# If full requirements.txt times out
pip install python-telegram-bot
pip install aiohttp
pip install dnspython
pip install google-generativeai  # For AI features
```

---

## 🛠️ Troubleshooting

### "Module not found: google.generativeai"

```bash
# Install the package
pip install google-generativeai

# Verify installation
python -c "import google.generativeai; print('OK')"
```

### "API key not configured"

```bash
# Check .env file exists
cat .env | grep GEMINI_API_KEY

# Or export temporarily
export GEMINI_API_KEY="your-key-here"
```

### "Permission denied: email-bot.sh"

```bash
# Make executable
chmod +x email-bot.sh

# Or run with bash
bash email-bot.sh
```

### Pip installation is slow/times out

```bash
# Use pip with shorter timeout
pip install --timeout=30 google-generativeai

# Or use mirrors
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple google-generativeai

# Or download wheel manually and install
pip install --no-deps google-generativeai
```

### "No templates found"

```bash
# Check templates directory
ls templates/

# Should see: flash_sale.html, modern_promo.html, etc.
# If empty, re-clone the repository
```

---

## 📁 Directory Structure After Setup

```
email-bot/
├── .env                        # Your config (created by you)
├── .env.example                # Template config
├── .gitignore                  # Git ignore rules
├── email-bot.sh                # Main CLI script
├── ai_template_generator.py    # AI template creator
├── opt_in_manager.py           # Double opt-in system
├── engagement_tracker.py       # Engagement tracking
├── domain_auth_checker.py      # Domain verification
├── compliance_footer.py        # Compliance footers
├── requirements.txt            # Dependencies
├── templates/                  # Email templates
│   ├── flash_sale.html
│   ├── modern_promo.html
│   └── ...
├── data/
│   ├── email_list.txt          # Your email list
│   ├── opt_in_subscribers.json # Confirmed subscribers
│   └── engagement.json         # Engagement data
└── logs/                       # Campaign logs
```

---

## ✅ Pre-Flight Checklist

Before sending your first campaign:

- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created and configured
- [ ] Gmail App Password generated (not regular password)
- [ ] Gemini API key added (for AI templates)
- [ ] Test modules run successfully
- [ ] Email list created in `data/email_list.txt`
- [ ] Domain authentication checked (SPF/DKIM/DMARC)

---

## 🎯 First Campaign Checklist

1. **Configure sender email**
   ```bash
   ./email-bot.sh
   # Settings > Configure Email Credentials
   ```

2. **Add recipients**
   ```bash
   ./email-bot.sh
   # Tools > Email List Manager > Add
   ```

3. **Create/select template**
   ```bash
   ./email-bot.sh
   # Templates > AI Template Generator
   ```

4. **Check spam score**
   ```bash
   python spam_checker.py your_template
   ```

5. **Send!**
   ```bash
   ./email-bot.sh
   # Send Emails > Send Bulk Campaign
   ```

---

## 📞 Getting Help

```bash
# View all commands
./email-bot.sh
# Help & Documentation

# Read guides
cat README.md
cat QUICK_USAGE.md
cat DELIVERABILITY_GUIDE.md
cat COMPLIANCE_QUICKSTART.md

# Check system status
./email-bot.sh
# Help > Check System Status
```

---

## 🎓 Next Steps

After setup is complete:

1. **Read the documentation**
   - `README.md` - Full feature list
   - `QUICK_USAGE.md` - Quick reference
   - `DELIVERABILITY_GUIDE.md` - Best practices

2. **Try the features**
   - Generate AI template
   - Set up double opt-in
   - Check domain authentication
   - Send test email

3. **Join the community** (if available)
   - Report bugs
   - Request features
   - Share templates

---

**Setup complete!** Run `./email-bot.sh` to start. 🎉
