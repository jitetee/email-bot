#!/usr/bin/env python3
"""Quick test email sender - uses credentials from .env."""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / '.env')

# Configuration from .env
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "")
RECIPIENT = os.getenv("TEST_RECIPIENT", "ezra2024w@gmail.com")
SUBJECT = "Test Email from Email Bot"

# Validate configuration
if not SENDER_EMAIL:
    print("❌ Error: SENDER_EMAIL not configured in .env")
    print("   Please edit .env and add your Gmail address")
    sys.exit(1)

if not SENDER_PASSWORD:
    print("❌ Error: SENDER_PASSWORD not configured in .env")
    print("   Please edit .env and add your Gmail App Password")
    sys.exit(1)

# HTML Body
HTML_BODY = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; }
        .container { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px; color: white; }
        h1 { margin: 0 0 20px 0; }
        .content { background: white; color: #333; padding: 30px; border-radius: 10px; margin-top: 20px; }
        .button { display: inline-block; background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 25px; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>✅ Test Email Successful!</h1>
    </div>
    <div class="content">
        <p>Hi there,</p>
        <p>This is a <strong>test email</strong> from the Email Bot system.</p>
        <p>If you received this, the email configuration is working correctly!</p>
        <a href="#" class="button">Visit Website</a>
        <p style="margin-top: 30px; color: #666;">
            Best regards,<br>
            <strong>Ezra</strong>
        </p>
    </div>
</body>
</html>"""

def send_test():
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = SUBJECT
        msg['From'] = f"Ezra <{SENDER_EMAIL}>"
        msg['To'] = RECIPIENT

        # Plain text version
        plain_text = "Test Email from Email Bot\n\nThis is a test message. If you received this, the configuration is working!"
        msg.attach(MIMEText(plain_text, 'plain', 'utf-8'))

        # HTML version
        msg.attach(MIMEText(HTML_BODY, 'html', 'utf-8'))

        # Connect and send
        print(f"\n📧 Connecting to Gmail SMTP...")
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            print(f"🔐 Authenticating as {SENDER_EMAIL}...")
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            print(f"📤 Sending to {RECIPIENT}...")
            server.send_message(msg)

        print("\n✅ SUCCESS! Email sent to", RECIPIENT)
        print("Check the inbox (and spam folder) for the test email.\n")
        return 0

    except smtplib.SMTPAuthenticationError:
        print("\n❌ Authentication failed!")
        print("Make sure you're using a Gmail App Password, not your regular password.")
        print("Get one at: https://myaccount.google.com/apppasswords")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(send_test())
