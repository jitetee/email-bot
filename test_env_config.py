#!/usr/bin/env python3
"""
Test that .env configuration is loaded correctly.
This script verifies SENDER_EMAIL and SENDER_PASSWORD are loaded from .env file.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("🔍 Testing .env Configuration Loading")
print("=" * 60)
print()

# Test 1: Check if .env file exists
env_file = Path(__file__).parent / '.env'
if env_file.exists():
    print("✅ .env file exists")
else:
    print("❌ .env file NOT found!")
    print("   Please create .env file or copy from .env.example")
    sys.exit(1)

# Test 2: Load configuration
print()
print("📖 Loading configuration from .env...")
try:
    from config import (
        SMTP_SERVER, 
        SMTP_PORT, 
        SENDER_EMAIL, 
        SENDER_PASSWORD, 
        SENDER_NAME
    )
    print("✅ Configuration loaded successfully")
except Exception as e:
    print(f"❌ Failed to load configuration: {e}")
    sys.exit(1)

# Test 3: Validate configuration values
print()
print("📋 Configuration Values:")
print("-" * 60)

# SMTP_SERVER
if SMTP_SERVER and SMTP_SERVER != "smtp.gmail.com":
    print(f"✅ SMTP_SERVER: {SMTP_SERVER}")
elif SMTP_SERVER == "smtp.gmail.com":
    print(f"⚙️  SMTP_SERVER: {SMTP_SERVER} (Gmail default)")
else:
    print(f"❌ SMTP_SERVER: Not configured")

# SMTP_PORT
print(f"✅ SMTP_PORT: {SMTP_PORT}")

# SENDER_EMAIL
if SENDER_EMAIL and SENDER_EMAIL != "your_email@gmail.com":
    print(f"✅ SENDER_EMAIL: {SENDER_EMAIL}")
else:
    print(f"❌ SENDER_EMAIL: Not configured (still using default)")
    print("   Edit .env and set your Gmail address")

# SENDER_PASSWORD
if SENDER_PASSWORD and SENDER_PASSWORD != "your_app_password_here":
    # Mask password for security
    masked = SENDER_PASSWORD[:4] + "*" * (len(SENDER_PASSWORD) - 4) if len(SENDER_PASSWORD) > 4 else "****"
    print(f"✅ SENDER_PASSWORD: {masked} (configured)")
else:
    print(f"❌ SENDER_PASSWORD: Not configured (still using default)")
    print("   Edit .env and add your Gmail App Password")
    print("   Get it from: https://myaccount.google.com/apppasswords")

# SENDER_NAME
if SENDER_NAME and SENDER_NAME != "Your Company":
    print(f"✅ SENDER_NAME: {SENDER_NAME}")
else:
    print(f"⚙️  SENDER_NAME: {SENDER_NAME} (default)")

print()
print("-" * 60)

# Test 4: Overall status
print()
if SENDER_EMAIL and SENDER_EMAIL != "your_email@gmail.com" and \
   SENDER_PASSWORD and SENDER_PASSWORD != "your_app_password_here":
    print("✅ CONFIGURATION COMPLETE!")
    print("   Your .env file is properly configured.")
    print("   You can now send real emails via SMTP.")
    print()
    print("🚀 Start the web app:")
    print("   ./start_web_app.sh")
    print()
    exit_code = 0
else:
    print("⚠️  CONFIGURATION INCOMPLETE!")
    print("   Please edit .env file and add:")
    print("   - SENDER_EMAIL (your Gmail address)")
    print("   - SENDER_PASSWORD (Gmail App Password)")
    print()
    print("📝 Edit .env:")
    print("   nano .env")
    print()
    print("🔗 Get Gmail App Password:")
    print("   https://myaccount.google.com/apppasswords")
    print()
    exit_code = 1

print("=" * 60)

sys.exit(exit_code)
