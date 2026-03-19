#!/usr/bin/env python3
"""Send a test email."""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "ezra2024w@gmail.com"
SENDER_PASSWORD = "eirf jfmd bzmf ezrj"
SENDER_NAME = "Ezra"

TO_EMAIL = "ezraogombo@gmail.com"
SUBJECT = "Test Email"
BODY = "This is a test email sent from the email bot."

def send_test_email():
    """Send a test email."""
    msg = MIMEMultipart()
    msg['Subject'] = SUBJECT
    msg['From'] = f"{SENDER_NAME} <{SENDER_EMAIL}>"
    msg['To'] = TO_EMAIL
    
    msg.attach(MIMEText(BODY, 'plain', 'utf-8'))
    
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        print("✓ Email sent successfully!")
        return True
    except Exception as e:
        print(f"✗ Failed to send email: {str(e)}")
        return False

if __name__ == "__main__":
    send_test_email()
