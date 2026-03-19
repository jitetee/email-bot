#!/usr/bin/env python3
"""Email sender CLI helper - handles actual email sending with smart delays."""

import argparse
import smtplib
import sys
import time
import random
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from datetime import datetime
from string import Template


def load_template(template_dir: Path, name: str) -> dict:
    """Load email template."""
    html_file = template_dir / f"{name}.html"
    subject_file = template_dir / f"{name}_subject.txt"

    if html_file.exists():
        with open(html_file, 'r', encoding='utf-8') as f:
            body = f.read()
    else:
        # Default template
        body = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; }
        .container { background: #f4f4f4; padding: 20px; border-radius: 10px; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
        .content { background: white; padding: 30px; }
        .cta-button { display: inline-block; background: #667eea; color: white; padding: 15px 40px; text-decoration: none; border-radius: 25px; margin: 20px 0; font-weight: bold; }
        .footer { background: #333; color: white; padding: 20px; text-align: center; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header"><h1>Special Offer!</h1></div>
        <div class="content">
            <p>Hi there,</p>
            <p>We have an exclusive offer just for you!</p>
            <center><a href="#" class="cta-button">Claim Offer</a></center>
        </div>
        <div class="footer">© 2026 Your Company. <a href="#" style="color:#aaa;">Unsubscribe</a></div>
    </div>
</body>
</html>"""

    if subject_file.exists():
        with open(subject_file, 'r', encoding='utf-8') as f:
            subject = f.read().strip()
    else:
        subject = "Special Offer Just for You!"

    return {'subject': subject, 'body': body}


def send_email(args, to_email: str, subject: str, html_body: str) -> bool:
    """Send a single email."""
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{args.name} <{args.email}>"
        msg['To'] = to_email

        # Plain text version
        import re
        plain = re.sub(r'<[^>]+>', '', html_body)
        msg.attach(MIMEText(plain, 'plain', 'utf-8'))

        # HTML version
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))

        # Send
        with smtplib.SMTP(args.smtp_server, args.smtp_port) as server:
            server.starttls()
            server.login(args.email, args.password)
            server.send_message(msg)

        return True
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return False


def get_random_delay(delay_min: float, delay_max: float) -> float:
    """Get random delay between min and max to avoid spam detection."""
    return random.uniform(delay_min, delay_max)


def send_single(args):
    """Send single email."""
    template_dir = Path(__file__).parent / 'templates'
    template = load_template(template_dir, args.template)

    # Apply variables
    variables = {
        'name': args.to.split('@')[0],
        'company': args.name,
        'link': '#',
        'unsubscribe_link': '#'
    }

    safe_subject = Template(template['subject']).safe_substitute(variables)
    safe_body = Template(template['body']).safe_substitute(variables)

    if args.subject:
        safe_subject = args.subject

    print(f"Sending to: {args.to}")
    print(f"Subject: {safe_subject}")

    if send_email(args, args.to, safe_subject, safe_body):
        print("✓ Sent successfully!")
        return 0
    else:
        print("✗ Failed to send")
        return 1


def send_bulk(args):
    """Send bulk emails with random delays to avoid spam detection."""
    template_dir = Path(__file__).parent / 'templates'
    template = load_template(template_dir, args.template)

    # Load email list
    if not Path(args.list).exists():
        print(f"Error: Email list not found: {args.list}", file=sys.stderr)
        return 1

    emails = []
    with open(args.list, 'r', encoding='utf-8') as f:
        for line in f:
            email = line.strip()
            if email and '@' in email:
                emails.append(email)

    if not emails:
        print("Error: No valid emails in list", file=sys.stderr)
        return 1

    print(f"Loaded {len(emails)} emails")
    print(f"Batch size: {args.batch_size}")
    print(f"Delay: Random {args.delay_min}-{args.delay_max}s between emails")
    print(f"Batch pause: {args.batch_delay}s")
    print("=" * 60)
    print(f"{args.bright}🛡️  SPAM AVOIDANCE MODE ENABLED{args.reset}")
    print(f"   Using random delays to mimic human behavior")
    print("=" * 60)

    # Stats
    sent = 0
    failed = 0
    start_time = datetime.now()

    # Create log file
    log_dir = Path(__file__).parent / 'logs'
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f"campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    with open(log_file, 'w') as log:
        log.write(f"Campaign started: {start_time}\n")
        log.write(f"Total emails: {len(emails)}\n")
        log.write(f"Delay range: {args.delay_min}-{args.delay_max}s (random)\n")
        log.write(f"Batch size: {args.batch_size}, Batch pause: {args.batch_delay}s\n\n")

        for i, email in enumerate(emails, 1):
            # Variables
            variables = {
                'name': email.split('@')[0],
                'company': args.name,
                'link': '#',
                'unsubscribe_link': '#'
            }

            safe_subject = Template(template['subject']).safe_substitute(variables)
            safe_body = Template(template['body']).safe_substitute(variables)

            if args.subject:
                safe_subject = args.subject

            # Send
            success = send_email(args, email, safe_subject, safe_body)

            if success:
                sent += 1
                status = "✓"
            else:
                failed += 1
                status = "✗"

            # Log
            log_line = f"[{i}/{len(emails)}] {status} {email}"
            print(log_line)
            log.write(log_line + "\n")

            # Progress
            if i % 10 == 0:
                elapsed = datetime.now() - start_time
                print(f"--- Progress: {i}/{len(emails)} (Sent: {sent}, Failed: {failed}) | Elapsed: {elapsed} ---")

            # Random delay between emails (anti-spam)
            if i < len(emails):
                delay = get_random_delay(args.delay_min, args.delay_max)
                delay_msg = f"⏱️  Waiting {delay:.1f}s..."
                print(delay_msg)
                log.write(f"  Delay: {delay:.1f}s\n")
                time.sleep(delay)

            # Delay between batches
            if i % args.batch_size == 0 and i < len(emails):
                batch_num = i // args.batch_size
                print(f"*** Batch {batch_num} complete. Pausing {args.batch_delay}s ***")
                log.write(f"--- Batch {batch_num} pause: {args.batch_delay}s ---\n")
                time.sleep(int(args.batch_delay))

    end_time = datetime.now()
    duration = end_time - start_time

    print("=" * 60)
    print(f"✓ Campaign Complete!")
    print(f"  Total: {len(emails)}")
    print(f"  Sent: {sent} ({sent/len(emails)*100:.1f}%)")
    print(f"  Failed: {failed} ({failed/len(emails)*100:.1f}%)")
    print(f"  Duration: {duration}")
    print(f"  Avg time per email: {duration.total_seconds()/len(emails):.2f}s")
    print(f"  Log: {log_file}")
    print("=" * 60)

    return 0


def main():
    # Color codes for output
    class Colors:
        BRIGHT = '\033[1m'
        RESET = '\033[0m'

    parser = argparse.ArgumentParser(
        description='Email Sender CLI with Smart Delays',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Single email:
    python email_sender_cli.py --email test@gmail.com --password xxx --template promo --single --to recipient@gmail.com
  
  Bulk with default delays:
    python email_sender_cli.py --email test@gmail.com --password xxx --template promo --bulk --list data/email_list.txt
  
  Bulk with custom random delays (anti-spam):
    python email_sender_cli.py --email test@gmail.com --password xxx --template promo --bulk --list data/email_list.txt --delay-min 2 --delay-max 5 --batch-size 20
        """
    )

    # SMTP settings
    parser.add_argument('--smtp-server', default='smtp.gmail.com', help='SMTP server (default: smtp.gmail.com)')
    parser.add_argument('--smtp-port', type=int, default=587, help='SMTP port (default: 587)')
    parser.add_argument('--email', required=True, help='Sender email address')
    parser.add_argument('--password', required=True, help='Sender app password')
    parser.add_argument('--name', default='Your Company', help='Sender name (default: Your Company)')

    # Template
    parser.add_argument('--template', default='modern_promo', help='Template name (default: modern_promo)')
    parser.add_argument('--subject', help='Custom subject (overrides template)')

    # Modes
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument('--single', action='store_true', help='Send single email')
    mode_group.add_argument('--bulk', action='store_true', help='Send bulk emails')

    # Single mode options
    parser.add_argument('--to', help='Recipient email (for single mode)')

    # Bulk mode options - Anti-spam delays
    parser.add_argument('--list', help='Email list file (for bulk mode)')
    parser.add_argument('--batch-size', type=int, default=25, 
                        help='Emails per batch before pause (default: 25)')
    parser.add_argument('--delay-min', type=float, default=1.0,
                        help='Minimum delay between emails in seconds (default: 1.0)')
    parser.add_argument('--delay-max', type=float, default=3.0,
                        help='Maximum delay between emails in seconds (default: 3.0)')
    parser.add_argument('--batch-delay', type=int, default=30,
                        help='Delay between batches in seconds (default: 30)')

    args = parser.parse_args()
    
    # Add color codes to args for use in output
    args.bright = Colors.BRIGHT
    args.reset = Colors.RESET

    if args.single:
        if not args.to:
            print("Error: --to required for single mode", file=sys.stderr)
            sys.exit(1)
        sys.exit(send_single(args))

    elif args.bulk:
        if not args.list:
            print("Error: --list required for bulk mode", file=sys.stderr)
            sys.exit(1)
        sys.exit(send_bulk(args))


if __name__ == '__main__':
    main()
