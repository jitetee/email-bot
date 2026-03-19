"""Bulk email sender with rate limiting and logging."""
import smtplib
import time
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from pathlib import Path
from typing import List, Optional, Callable
from datetime import datetime

from config import (
    SMTP_SERVER, SMTP_PORT, SENDER_EMAIL, SENDER_PASSWORD,
    SENDER_NAME, BATCH_SIZE, DELAY_BETWEEN_BATCHES,
    DELAY_BETWEEN_EMAILS, LOGS_DIR, IMAGES_DIR
)


class BulkEmailSender:
    """Send bulk emails with rate limiting and progress tracking."""
    
    def __init__(self):
        self.logger = self._setup_logger()
        self.stats = {
            'sent': 0,
            'failed': 0,
            'total': 0,
            'start_time': None,
            'end_time': None
        }
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logging to file and console."""
        logger = logging.getLogger('email_sender')
        logger.setLevel(logging.INFO)
        
        # File handler
        log_file = LOGS_DIR / f"email_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def load_email_list(self, file_path: Path) -> List[str]:
        """Load email addresses from a text file (one per line)."""
        if not file_path.exists():
            raise FileNotFoundError(f"Email list file not found: {file_path}")
        
        emails = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                email = line.strip()
                if email and '@' in email:
                    emails.append(email)
        
        self.logger.info(f"Loaded {len(emails)} emails from {file_path}")
        return emails
    
    def create_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None,
        image_path: Optional[Path] = None
    ) -> MIMEMultipart:
        """Create a MIME email message."""
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{SENDER_NAME} <{SENDER_EMAIL}>"
        msg['To'] = to_email
        
        # Add text version (for email clients that don't support HTML)
        if text_body:
            msg.attach(MIMEText(text_body, 'plain', 'utf-8'))
        else:
            # Generate plain text from HTML (basic stripping)
            import re
            plain = re.sub(r'<[^>]+>', '', html_body)
            msg.attach(MIMEText(plain, 'plain', 'utf-8'))
        
        # Add HTML version
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))
        
        # Attach image if provided
        if image_path and image_path.exists():
            with open(image_path, 'rb') as img_file:
                img = MIMEImage(img_file.read())
                img.add_header('Content-ID', '<promo-image>')
                img.add_header('Content-Disposition', 'inline', filename=image_path.name)
                msg.attach(img)
        
        return msg
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None,
        image_path: Optional[Path] = None
    ) -> bool:
        """Send a single email."""
        try:
            msg = self.create_email(to_email, subject, html_body, text_body, image_path)
            
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SENDER_EMAIL, SENDER_PASSWORD)
                server.send_message(msg)
            
            self.logger.info(f"✓ Sent to: {to_email}")
            self.stats['sent'] += 1
            return True
            
        except Exception as e:
            self.logger.error(f"✗ Failed to {to_email}: {str(e)}")
            self.stats['failed'] += 1
            return False
    
    def send_bulk(
        self,
        emails: List[str],
        subject: str,
        html_body: str,
        text_body: Optional[str] = None,
        image_path: Optional[Path] = None,
        progress_callback: Optional[Callable[[int, int, int], None]] = None
    ) -> dict:
        """Send emails in bulk with rate limiting.
        
        Args:
            emails: List of recipient email addresses
            subject: Email subject
            html_body: HTML email body
            text_body: Plain text version (optional)
            image_path: Path to image attachment (optional)
            progress_callback: Function(current, total, status) for progress updates
            
        Returns:
            dict with sending statistics
        """
        self.stats = {
            'sent': 0,
            'failed': 0,
            'total': len(emails),
            'start_time': datetime.now(),
            'end_time': None
        }
        
        self.logger.info(f"Starting bulk send to {len(emails)} recipients")
        self.logger.info(f"Batch size: {BATCH_SIZE}, Delay: {DELAY_BETWEEN_EMAILS}s")
        
        for i, email in enumerate(emails, 1):
            # Progress callback
            if progress_callback:
                progress_callback(i, len(emails), 'sending')
            
            # Send email
            self.send_email(email, subject, html_body, text_body, image_path)
            
            # Delay between emails
            if i < len(emails):
                time.sleep(DELAY_BETWEEN_EMAILS)
            
            # Delay between batches
            if i % BATCH_SIZE == 0 and i < len(emails):
                self.logger.info(f"--- Batch {i // BATCH_SIZE} complete. Pausing {DELAY_BETWEEN_BATCHES}s ---")
                if progress_callback:
                    progress_callback(i, len(emails), 'batch_pause')
                time.sleep(DELAY_BETWEEN_BATCHES)
        
        self.stats['end_time'] = datetime.now()
        duration = self.stats['end_time'] - self.stats['start_time']
        
        self.logger.info("=" * 50)
        self.logger.info("Campaign Complete!")
        self.logger.info(f"Total: {self.stats['total']} | Sent: {self.stats['sent']} | Failed: {self.stats['failed']}")
        self.logger.info(f"Duration: {duration}")
        self.logger.info("=" * 50)
        
        return self.stats
    
    def get_stats(self) -> dict:
        """Get current sending statistics."""
        return self.stats.copy()
