```
 ███████╗███╗   ███╗ █████╗ ██╗██╗     ██████╗  ██████╗ ████████╗
 ██╔════╝████╗ ████║██╔══██╗██║██║     ██╔══██╗██╔═══██╗╚══██╔══╝
 █████╗  ██╔████╔██║███████║██║██║     ██████╔╝██║   ██║   ██║
 ██╔══╝  ██║╚██╔╝██║██╔══██║██║██║     ██╔══██╗██║   ██║   ██║
 ███████╗██║ ╚═╝ ██║██║  ██║██║███████╗██████╔╝╚██████╔╝   ██║
 ╚══════╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝╚══════╝╚═════╝  ╚═════╝    ╚═╝
   Email Marketing Platform — SMTP Campaigns, Templates, Analytics
                  a Kashsight project by @kashsight
```

# 📧 Email Bot v3.0 - Professional Email Marketing Platform

<div align="center">

![Email Bot Banner](https://img.shields.io/badge/Email_Bot-v3.0-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8+-green?style=for-the-badge&logo=python)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)
![Stars](https://img.shields.io/github/stars/kashsight/email-bot?style=for-the-badge)

**A powerful, compliant email marketing platform with AI-powered templates**

[![Features](https://img.shields.io/badge/Features-Complete-brightgreen?style=for-the-badge)](#-features)
[![Quick Start](https://img.shields.io/badge/Quick_Start-Guide-orange?style=for-the-badge)](#-quick-start)
[![Documentation](https://img.shields.io/badge/Documentation-Full-blue?style=for-the-badge)](#-documentation)

</div>

---

## 🌟 Features

<div align="center">

| 📤 **Bulk Sending** | 🎨 **Beautiful Templates** | ⚙️ **Smart Automation** |
|:---:|:---:|:---:|
| Send 10,000+ emails with rate limiting | 20+ professional HTML templates | Schedule campaigns in advance |

| 🔐 **Domain Authentication** | 📊 **Analytics Dashboard** | ✅ **Compliance Tools** |
|:---:|:---:|:---:|
| SPF, DKIM, DMARC verification | Real-time campaign statistics | GDPR & CAN-SPAM compliant |

| 🤖 **Telegram Bot** | 🔄 **SMTP Rotation** | 🌡️ **Warm-up Mode** |
|:---:|:---:|:---:|
| Control from Telegram | Multiple SMTP accounts | Build sender reputation |

</div>

---

## 🚀 Quick Start

### One-Line Installation

```bash
git clone https://github.com/kashsight/email-bot.git && cd email-bot && chmod +x install.sh && ./install.sh
```

### Step-by-Step Installation

```bash
# 1. Clone the repository
git clone https://github.com/kashsight/email-bot.git
cd email-bot

# 2. Run the installation script
chmod +x install.sh
./install.sh

# 3. Configure your credentials
nano .env

# 4. Start sending emails!
./email-bot.sh
```

---

## ⚙️ Configuration

### 1. Get Gmail App Password

1. Go to [Google Account](https://myaccount.google.com/)
2. Enable **2-Factor Authentication**
3. Visit [App Passwords](https://myaccount.google.com/apppasswords)
4. Select "Mail" and your device
5. Copy the 16-character password

### 2. Edit `.env` File

```bash
nano .env
```

```env
# Email Configuration
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD="your_16_char_app_password"
SENDER_NAME=Your Name

# SMTP Settings
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# Sending Settings
BATCH_SIZE=25
DELAY_MIN=1
DELAY_MAX=3
```

---

## 📖 Usage

### Interactive Menu

```bash
./email-bot.sh
```

<div align="center">
  
```
╔═══════════════════════════════════════════════════════════╗
║           📧 Email Bot v3.0 - Enhanced CLI                ║
║     Compliance • Smart Sending • Easy Management          ║
╚═══════════════════════════════════════════════════════════╝

═══════════════════════════════════════════════════════════
                    MAIN MENU                                
═══════════════════════════════════════════════════════════
  [1] 📤 Send Emails
  [2] 🎨 Templates
  [3] 📊 Analytics & Reports
  [4] ⚙️  Settings & Configuration
  [5] 🛠️  Tools & Utilities
  [6] 🚀 Quick Start Server
  [7] 📖 Help & Documentation
  [0] Exit
═══════════════════════════════════════════════════════════
```

</div>

### Send Test Email

```bash
python test_email.py
```

### View Statistics

```bash
python stats_dashboard.py
```

---

## 🛠️ Command Reference

### Email Sending

```bash
# Send single email
./email-bot.sh
# Select: Send Emails > Send Single Email

# Send bulk campaign
./email-bot.sh
# Select: Send Emails > Send Bulk Campaign

# Send test email
python test_email.py
```

### List Management

```bash
# View email list stats
python email_list_manager.py stats

# Add email
python email_list_manager.py add user@example.com

# Clean invalid emails
python email_list_manager.py clean

# Remove duplicates
python email_list_manager.py dedup

# Import from CSV
python email_list_manager.py import contacts.csv
```

### Analytics

```bash
# Statistics dashboard
python stats_dashboard.py

# Engagement tracking
python engagement_tracker.py segment

# Bounce reports
python bounce_handler.py stats

# A/B test results
python ab_test_manager.py list
```

### Compliance Tools

```bash
# Domain authentication check
python domain_auth_checker.py yourdomain.com

# Spam score check
python spam_checker.py template_name

# Generate compliance footer
python compliance_footer.py

# Double opt-in management
python opt_in_manager.py stats
```

---

## 📁 Project Structure

```
email-bot/
├── 📄 email-bot.sh              # Main CLI script
├── 📄 install.sh                # Installation script
├── 📄 requirements.txt          # Python dependencies
├── 📄 .env.example              # Configuration template
├── 📄 README.md                 # This file
│
├── 📂 Python Modules
│   ├── config.py                # Configuration loader
│   ├── email_sender.py          # Bulk email sender
│   ├── email_validator.py       # Email validation
│   ├── spam_checker.py          # Spam score checker
│   ├── bounce_handler.py        # Bounce tracking
│   ├── engagement_tracker.py    # Engagement scoring
│   ├── opt_in_manager.py        # Double opt-in
│   ├── domain_auth_checker.py   # SPF/DKIM/DMARC
│   ├── compliance_footer.py     # Compliance footers
│   ├── stats_dashboard.py       # Analytics dashboard
│   ├── template_manager.py      # Template management
│   └── ... (20+ modules)
│
├── 📂 templates/                # Email templates
│   ├── flash_sale.html
│   ├── modern_promo.html
│   └── ... (20+ templates)
│
├── 📂 data/
│   ├── email_list.txt           # Recipient emails
│   └── images/                  # Email images
│
└── 📂 logs/                     # Campaign logs
```

---

## 🔒 Security

### Protected Files

The following are **automatically ignored** by git:

```
.env                    # Credentials
*.key                   # API keys
*.secret                # Secrets
data/*.json            # Generated data
logs/*.log             # Logs
```

### Best Practices

✅ Use **App Passwords**, not regular passwords  
✅ Keep `.env` file private  
✅ Never commit credentials to git  
✅ Use double opt-in for subscribers  
✅ Include unsubscribe links  

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [README.md](README.md) | Full documentation |
| [QUICK_USAGE.md](QUICK_USAGE.md) | Quick reference guide |
| [SETUP_GUIDE.md](SETUP_GUIDE.md) | Detailed setup instructions |
| [DELIVERABILITY_GUIDE.md](DELIVERABILITY_GUIDE.md) | Best practices |
| [COMPLIANCE_QUICKSTART.md](COMPLIANCE_QUICKSTART.md) | Legal compliance |

---

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) first.

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## ☕ Support

If you find this project helpful, consider supporting its development!

<div align="center">

### [💖 Donate via PayPal](https://paypal.me/yourusername)

### [🌟 Sponsor on GitHub](https://github.com/sponsors/kashsight)

### [☕ Buy Me a Coffee](https://buymeacoffee.com/yourusername)

</div>

**Your support helps keep this project maintained and growing!**

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2026 Ezra Ogombo

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 📬 Contact

<div align="center">

**Ezra Ogombo**

[![GitHub](https://img.shields.io/badge/GitHub-kashsight-blue?style=for-the-badge&logo=github)](https://github.com/kashsight)
[![Email](https://img.shields.io/badge/Email-Contact-red?style=for-the-badge&logo=gmail)](mailto:kashsight@gmail.com)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue?style=for-the-badge&logo=linkedin)](https://linkedin.com/in/kashsight)

**Made with ❤️ by Ezra Ogombo**

</div>

---

<div align="center">

### ⭐ If you like this project, please give it a star!

![Stars](https://img.shields.io/github/stars/kashsight/email-bot?style=for-the-badge)
![Forks](https://img.shields.io/github/forks/kashsight/email-bot?style=for-the-badge)
![Issues](https://img.shields.io/github/issues/kashsight/email-bot?style=for-the-badge)

</div>
