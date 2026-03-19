# ✅ Credentials Auto-Load - Update Complete

## What Changed

The bash script now **automatically loads** your email credentials from `.env` instead of asking every time.

---

## How It Works

### Before (Old Behavior)
```bash
./email-bot.sh
# Every time: Enter sender email, Enter password, Enter name...
```

### After (New Behavior)
```bash
./email-bot.sh
# ✓ Using saved credentials: ezra2024w@gmail.com
# Use saved credentials? (Y/n): Y  ← Just press Enter!
```

---

## Features

### 1. Auto-Load from `.env`

Your credentials in `.env` are now used automatically:
- `SENDER_EMAIL` - Your email address
- `SENDER_PASSWORD` - Your app password
- `SENDER_NAME` - Your sender name

### 2. Option to Override

You can still use different credentials if needed:
```
✓ Using saved credentials: ezra2024w@gmail.com
Use saved credentials? (Y/n): n  ← Type 'n' to use different credentials
```

### 3. Settings Menu Shows Current Values

```bash
./email-bot.sh
# Settings > Configure Email Credentials

Current settings from .env:
  Email: ezra2024w@gmail.com
  Name:  Ezra
  SMTP:  smtp.gmail.com:587

Press Enter to keep current value
```

---

## Your Current Configuration

**From `.env`:**
```
Email: ezra2024w@gmail.com
Password: ******** (19 chars)
Name: Ezra
SMTP: smtp.gmail.com:587
```

---

## Quick Test

```bash
# Start the menu
./email-bot.sh

# Go to: Send Emails > Send Bulk Campaign
# You'll see: ✓ Using saved credentials: ezra2024w@gmail.com
# Press Enter to use them!
```

---

## Update Settings

To change your default credentials:

```bash
./email-bot.sh
# 4. Settings > Configure Email Credentials
# Edit values (press Enter to keep current)
# 6. Save Configuration
```

Or edit `.env` directly:
```bash
nano .env
# Update SENDER_EMAIL, SENDER_PASSWORD, etc.
# Save and restart the script
```

---

## Security Notes

✅ **`.env` is in `.gitignore`** - Won't be committed to git  
✅ **Password quoted properly** - Handles spaces in passwords  
✅ **Hidden input** - Password not shown when typing  
✅ **Option to override** - Can use different credentials per campaign  

⚠️ **Still keep `.env` private** - Contains real passwords  
⚠️ **Use App Passwords** - Not your regular email password  

---

## Troubleshooting

### "Credentials not loading"

Check `.env` file format:
```bash
# Correct:
SENDER_PASSWORD="password with spaces"

# Wrong:
SENDER_PASSWORD=password with spaces  # Missing quotes!
```

### "Script doesn't start"

Make sure it's executable:
```bash
chmod +x email-bot.sh
./email-bot.sh
```

### "Want to reset to defaults"

Edit `.env`:
```bash
nano .env
# Delete or comment out lines
# Restart script
```

---

## What's Protected

These files are **ignored by git**:

```
.env                    ← Your credentials
.env.*                  ← All env variants
*.key                   ← API keys
*.secret                ← Secrets
data/*.json            ← Generated data
logs/*.log             ← Logs
```

---

**Status:** ✅ Complete  
**Updated:** email-bot.sh  
**Date:** 2026-03-19
