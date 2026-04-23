# 📧 Email Bot v5.0 - Quick Start Guide

## ✅ What's New in v5.0

- **REAL EMAIL SENDING**: Web interface now sends REAL emails via SMTP (not demo/fake)
- **Enhanced Setup**: New `setup.bash` script for complete installation
- **Error-Free Web Version**: `web_app_enhanced.py` is the stable, error-free version
- **Both Web Apps Updated**: Both `web_app.py` and `web_app_enhanced.py` send real emails

---

## 🚀 Quick Installation

### Option 1: Using setup.bash (RECOMMENDED)

```bash
# Run the complete setup script
./setup.bash
```

### Option 2: Manual Installation

```bash
# Install Python packages
pip3 install -r requirements.txt

# Create directories
mkdir -p data/images logs templates

# Copy environment file
cp .env.example .env

# Edit configuration
nano .env
```

---

## ⚙️ Configuration

### 1. Edit .env File

```bash
nano .env
```

### 2. Required Settings

```ini
# SMTP Settings (Gmail Example)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password_here
SENDER_NAME=Your Company

# Bulk Email Settings
BATCH_SIZE=25
DELAY_MIN=1.0
DELAY_MAX=3.0
```

### 3. Get Gmail App Password

1. Go to: https://myaccount.google.com/apppasswords
2. Select "Mail" and your device
3. Copy the 16-character password
4. Paste it in `.env` as `SENDER_PASSWORD`

---

## 🌐 Starting the Web Application

### Recommended: Enhanced Version (Error-Free)

```bash
./start_web_app.sh
```

Or specify a different port:

```bash
./start_web_app.sh 9000
```

Then open: **http://localhost:8080**

### Alternative: Classic Version

```bash
python3 web_app.py 8080
```

---

## 📤 Sending Real Emails

### Single Email

1. Go to "Send Emails" → "Single Email"
2. Enter recipient email
3. Enter subject
4. Select template or write content
5. Click "Send"
6. ✅ Email sent via REAL SMTP!

### Bulk Campaign

1. Add emails to `data/email_list.txt` (one per line)
2. Go to "Send Emails" → "Bulk Campaign"
3. Select template
4. Enter subject
5. Set batch size (25 recommended)
6. Click "Send Bulk"
7. ✅ Real emails sent with rate limiting!

---

## 📋 Email List Management

### Add Emails Manually

```bash
nano data/email_list.txt
```

Add one email per line:
```
recipient1@example.com
recipient2@example.com
```

### Import from CSV

Use the web interface: "Email List" → "Import"

---

## 🎨 Template Management

### Create Template

1. Go to "Templates" → "Create New"
2. Enter template name
3. Write HTML content
4. Click "Create"

### Use Pre-made Templates

Check the `templates/` folder for sample templates.

---

## 🔧 Troubleshooting

### SMTP Authentication Failed

**Problem**: "SMTP Authentication failed"

**Solution**:
- Use Gmail App Password, NOT regular password
- Get it from: https://myaccount.google.com/apppasswords
- Make sure 2FA is enabled on your Google account

### Connection Error

**Problem**: "SMTP Connection failed"

**Solution**:
- Check SMTP_SERVER setting (should be `smtp.gmail.com` for Gmail)
- Check SMTP_PORT (should be `587` for TLS)
- Check firewall settings

### No Emails in List

**Problem**: "No emails in list"

**Solution**:
- Add emails to `data/email_list.txt`
- One email per line
- Lines starting with `#` are comments

---

## 📊 Features Overview

### Email Sending
- ✅ Single email sending via REAL SMTP
- ✅ Bulk campaigns with rate limiting
- ✅ Scheduled campaigns
- ✅ Test email sending

### Template Management
- ✅ Browse templates
- ✅ Create new templates
- ✅ Edit templates
- ✅ Preview templates
- ✅ Import HTML templates
- ✅ Customize templates

### Email List Management
- ✅ Add emails
- ✅ Remove emails
- ✅ Validate emails
- ✅ Clean invalid emails
- ✅ Import from CSV
- ✅ Export to CSV
- ✅ Remove duplicates

### Advanced Features
- ✅ SMTP warm-up mode
- ✅ A/B testing
- ✅ Multiple SMTP accounts
- ✅ Domain authentication check
- ✅ Spam score checker
- ✅ Double opt-in manager
- ✅ Compliance footer generator
- ✅ CSS injector
- ✅ Email signatures
- ✅ Signup forms
- ✅ Preheaders
- ✅ Image management
- ✅ Link tracking

---

## 🛑 Stopping the Web Server

Press **Ctrl+C** in the terminal to stop the web application.

---

## 📚 Documentation

- `README.md` - Full documentation
- `SETUP_GUIDE.md` - Detailed setup guide
- `QUICK_USAGE.md` - Quick reference
- `DELIVERABILITY_GUIDE.md` - Email deliverability tips

---

## ⚠️ Important Notes

1. **Always use App Passwords** for Gmail (not regular passwords)
2. **Start with small batches** (10-25 emails) to avoid spam filters
3. **Use warm-up mode** for new email accounts
4. **Respect email laws** (GDPR, CAN-SPAM, etc.)
5. **Don't send unsolicited emails** (only send to opted-in recipients)

---

## 🎯 Quick Commands Reference

```bash
# Setup
./setup.bash                    # Complete installation

# Start Web Application
./start_web_app.sh              # Enhanced version (recommended)
./start_web_app.sh 9000         # Custom port

# CLI Interface
./email-bot.sh                  # Interactive menu

# API Server
python3 api_server.py           # REST API

# Direct Python
python3 web_app_enhanced.py     # Enhanced web app
python3 web_app.py              # Classic web app
```

---

## ✨ Success Indicators

When emails are sent successfully, you'll see:

- ✅ "Email sent successfully via SMTP!"
- ✅ "Bulk send completed: X sent, Y failed"
- ✅ Logs in `logs/` directory
- ✅ Real emails received in inbox (check spam folder too)

---

**Happy Emailing! 📧**
