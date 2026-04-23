"""Configuration settings for the email bot."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file explicitly
BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / '.env')

# Base directory
BASE_DIR = Path(__file__).parent

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# Email Configuration
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "")
SENDER_NAME = os.getenv("SENDER_NAME", "Your Company")

# Bulk Email Settings - Anti-Spam Configuration
# Using random delays helps avoid Gmail's spam detection for mass sending

BATCH_SIZE = int(os.getenv("BATCH_SIZE", "25"))  # Emails per batch (lower = safer)

DELAY_BETWEEN_BATCHES = int(os.getenv("DELAY_BETWEEN_BATCHES", "30"))  # Seconds between batches

# Random delay range for each email (prevents pattern detection)
DELAY_BETWEEN_EMAILS = float(os.getenv("DELAY_BETWEEN_EMAILS", "1.0"))  # Base delay
DELAY_MIN = float(os.getenv("DELAY_MIN", "1.0"))  # Minimum random delay
DELAY_MAX = float(os.getenv("DELAY_MAX", "3.0"))  # Maximum random delay

# Recommended settings for different sending volumes:
# Small (1-50 emails):   DELAY_MIN=1, DELAY_MAX=3, BATCH_SIZE=25
# Medium (50-200):       DELAY_MIN=2, DELAY_MAX=5, BATCH_SIZE=20
# Large (200-500):       DELAY_MIN=3, DELAY_MAX=8, BATCH_SIZE=15
# Very Large (500+):     DELAY_MIN=5, DELAY_MAX=15, BATCH_SIZE=10

# File Paths
DATA_DIR = BASE_DIR / "data"
EMAIL_LIST_FILE = BASE_DIR / "data" / "email_list.txt"
TEMPLATES_DIR = BASE_DIR / "templates"
LOGS_DIR = BASE_DIR / "logs"
IMAGES_DIR = BASE_DIR / "data" / "images"
ERROR_LOG_FILE = BASE_DIR / "logs" / "web_errors.log"

# Ensure directories exist
LOGS_DIR.mkdir(exist_ok=True)
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

# Email Template Defaults
DEFAULT_SUBJECT = "Special Offer Just for You!"
DEFAULT_FROM_NAME = SENDER_NAME

# Validation
if not SENDER_EMAIL or SENDER_EMAIL == "your_email@gmail.com":
    print("⚠️  WARNING: SENDER_EMAIL not configured in .env")
    print("   Please edit .env and add your Gmail address")
    
if not SENDER_PASSWORD or SENDER_PASSWORD == "your_app_password":
    print("⚠️  WARNING: SENDER_PASSWORD not configured in .env")
    print("   Please edit .env and add your Gmail App Password")
