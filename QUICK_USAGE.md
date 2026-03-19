# 🚀 Quick Usage Guide - Email Bot v3.0

## ⚡ Quick Start Commands

### Start the Interactive Menu
```bash
./email-bot.sh
```

### Auto-Start Services
```bash
# Choose what to start (server, bot, or both)
./email-bot.sh --auto

# Start API server directly
./email-bot.sh --server

# Start Telegram bot directly
./email-bot.sh --bot
```

---

## 📱 Menu Navigation

### Main Menu Options

| Key | Action | Description |
|-----|--------|-------------|
| 1 | 📤 Send Emails | Send single or bulk emails |
| 2 | 🎨 Templates & AI | Browse, create, edit templates |
| 3 | 📊 Analytics | View stats and reports |
| 4 | ⚙️ Settings | Configure email, delays, domain auth |
| 5 | 🛠️ Tools | Email list, validator, spam checker |
| 6 | 🚀 Quick Start Server | Start API server on port 8080 |
| 7 | 📖 Help | Guides and documentation |

---

## ✨ AI Template Generator

### Setup
1. Get Gemini API key: https://makersuite.google.com/app/apikey
2. Add to `.env`:
   ```
   GEMINI_API_KEY=your-api-key-here
   ```

### Generate Template via Menu
```bash
./email-bot.sh
# Go to: Templates & AI > AI Template Generator
```

### Generate Template via Command
```bash
python ai_template_generator.py "Summer sale with 50% off all products"
```

### With Custom Name and Style
```bash
python ai_template_generator.py "Welcome new subscribers" welcome_email friendly
```

### Available Styles
- `modern` - Clean, gradients, rounded corners
- `minimal` - Lots of white space, simple
- `bold` - High contrast, attention-grabbing
- `elegant` - Sophisticated, premium feel
- `dark` - Dark mode, neon accents
- `friendly` - Warm colors, approachable
- `corporate` - Professional, trustworthy
- `playful` - Colorful, fun, emoji-friendly

---

## 📧 Send Your First Campaign

### Option 1: Interactive Menu (Recommended)
```bash
./email-bot.sh
# 1. Send Emails > Send Bulk Campaign
# Follow prompts for email, password, template, subject
```

### Option 2: Command Line
```bash
./email-bot.sh --bulk \
  --email your_email@gmail.com \
  --password your_app_password \
  --template modern_promo \
  --subject "Special Offer!"
```

### Option 3: API Server
```bash
# Start server
./email-bot.sh --server

# Send via API
curl -X POST http://localhost:8080/api/send \
  -H "Content-Type: application/json" \
  -d '{
    "to": "user@example.com",
    "template": "modern_promo",
    "subject": "Hello!"
  }'
```

---

## 🛡️ Compliance Tools

### Double Opt-In (GDPR Compliant)
```bash
./email-bot.sh
# Tools > Double Opt-In Manager

# Or via command
python opt_in_manager.py subscribe user@example.com
python opt_in_manager.py confirm <token>
python opt_in_manager.py stats
```

### Check Domain Authentication
```bash
./email-bot.sh
# Settings > Domain Authentication

# Or via command
python domain_auth_checker.py yourdomain.com
```

### Generate Compliant Footer
```bash
./email-bot.sh
# Tools > Compliance Footer Generator

# Or via command
python compliance_footer.py
```

### Check Spam Score
```bash
./email-bot.sh
# Tools > Spam Score Checker

# Or via command
python spam_checker.py your_template
```

---

## 📊 Analytics & Tracking

### View Dashboard
```bash
./email-bot.sh
# Analytics > Statistics Dashboard
```

### Engagement Tracking
```bash
./email-bot.sh
# Analytics > Engagement Tracker

# View segments by engagement level
python engagement_tracker.py segment

# Find inactive subscribers
python engagement_tracker.py inactive 90

# Top engaged subscribers
python engagement_tracker.py top 20
```

---

## ⚙️ Essential Configuration

### 1. Email Credentials
```bash
./email-bot.sh
# Settings > Configure Email Credentials
```

Or edit `.env`:
```env
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

### 2. Delay Settings (Spam Avoidance)
```bash
./email-bot.sh
# Settings > Configure Delay Settings
```

Recommended settings:
- **Small lists (1-50)**: DELAY_MIN=1, DELAY_MAX=3
- **Medium lists (50-200)**: DELAY_MIN=2, DELAY_MAX=5
- **Large lists (200+)**: DELAY_MIN=3, DELAY_MAX=8

### 3. AI Template API Key
```env
GEMINI_API_KEY=your-gemini-api-key
```

---

## 🎯 Common Workflows

### Workflow 1: Quick Single Email
```bash
./email-bot.sh
1. Send Emails > Send Single Email
2. Enter recipient, template, subject
3. Done!
```

### Workflow 2: Full Campaign
```bash
# 1. Clean email list
./email-bot.sh
Tools > Email List Manager > Clean

# 2. Check spam score
./email-bot.sh
Tools > Spam Score Checker

# 3. Send campaign
./email-bot.sh
Send Emails > Send Bulk Campaign
```

### Workflow 3: AI Template Creation
```bash
# 1. Generate template with AI
./email-bot.sh
Templates > AI Template Generator
Describe: "Product launch announcement"

# 2. Preview template
./email-bot.sh
Templates > Preview Template

# 3. Send using new template
./email-bot.sh
Send Emails > Send Bulk Campaign
```

---

## 🔧 Useful Commands

### Email List Management
```bash
# Add email
python email_list_manager.py add user@example.com

# View stats
python email_list_manager.py stats

# Remove invalid emails
python email_list_manager.py clean

# Remove duplicates
python email_list_manager.py dedup

# Import from CSV
python email_list_manager.py import contacts.csv

# Export to CSV
python email_list_manager.py export clean_list.csv
```

### Template Management
```bash
# List all templates
python template_preview.py

# Preview specific template
python template_preview.py template_name

# Clone template
python template_manager.py clone modern_promo my_promo

# Search templates
python template_manager.py search "sale"
```

### Warm-up New Account
```bash
# Start warm-up
python warmup_manager.py start new_email@gmail.com

# Check status
python warmup_manager.py status <session_id>
```

---

## 📚 Documentation Files

| File | Description |
|------|-------------|
| `README.md` | Full documentation |
| `COMPLIANCE_QUICKSTART.md` | Legal compliance guide |
| `DELIVERABILITY_GUIDE.md` | Best practices for inbox delivery |
| `QUICK_USAGE.md` | This file - quick reference |

---

## 🆘 Troubleshooting

### No Password/Login Failed
- Use **App Password**, not regular password
- Enable 2FA on Google account first
- Generate app password: https://myaccount.google.com/apppasswords

### Emails Going to Spam
1. Check domain auth: `python domain_auth_checker.py yourdomain.com`
2. Check spam score: `python spam_checker.py template`
3. Increase delays between emails
4. Use warm-up mode for new accounts

### AI Template Generator Not Working
- Check API key: `echo $GEMINI_API_KEY`
- Get key from: https://makersuite.google.com/app/apikey
- Add to `.env`: `GEMINI_API_KEY=your-key`

### Server Won't Start
- Check if port 8080 is in use
- Try different port: `python api_server.py --port 8081`

---

## 💡 Pro Tips

1. **Always use double opt-in** for new subscribers (GDPR compliance)
2. **Check spam score** before every campaign
3. **Segment by engagement** - don't send to inactive users
4. **Warm up new accounts** gradually over 2-4 weeks
5. **Authenticate your domain** (SPF/DKIM/DMARC)
6. **Use AI templates** for professional designs
7. **Monitor bounce rate** - keep under 2%
8. **Start API server** for web dashboard access

---

## 🎓 Learning Path

### Beginner
1. Configure email credentials
2. Send test email
3. Browse templates
4. Send first campaign

### Intermediate
1. Set up double opt-in
2. Check domain authentication
3. Use AI template generator
4. View engagement stats

### Advanced
1. A/B testing
2. SMTP account rotation
3. Custom CSS injection
4. API integrations

---

**Need more help?** Run `./email-bot.sh` and go to **Help & Documentation**
