#!/usr/bin/env python3
"""
Email Bot Web Application v5.0 - Enhanced Edition
Advanced template editor, image management, link tracking, enhanced email sending

⚠️  REAL EMAIL SENDING - NOT DEMO/FAKE
    This application sends REAL emails via SMTP using Python's smtplib.
    Configure your SMTP credentials in .env file before use.
    
    Required .env settings:
    - SMTP_SERVER (e.g., smtp.gmail.com)
    - SMTP_PORT (e.g., 587)
    - SENDER_EMAIL (your Gmail address)
    - SENDER_PASSWORD (Gmail App Password, NOT regular password)
    - SENDER_NAME (your company name)
    
    Get Gmail App Password: https://myaccount.google.com/apppasswords
"""

import json
import os
import sys
import base64
import re
import time
from pathlib import Path
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import html

sys.path.insert(0, str(Path(__file__).parent))

# Import configuration from .env via config.py
from config import (
    TEMPLATES_DIR, 
    EMAIL_LIST_FILE, 
    LOGS_DIR, 
    DATA_DIR, 
    IMAGES_DIR, 
    ERROR_LOG_FILE, 
    SMTP_SERVER, 
    SMTP_PORT, 
    SENDER_EMAIL, 
    SENDER_PASSWORD, 
    SENDER_NAME
)

# Validate configuration
if not SENDER_EMAIL or SENDER_EMAIL == "your_email@gmail.com":
    print("⚠️  WARNING: SENDER_EMAIL not configured in .env file!")
    print("   Please edit .env and add your Gmail address")
    print("   The web app will not be able to send emails without this.")

if not SENDER_PASSWORD or SENDER_PASSWORD == "your_app_password_here":
    print("⚠️  WARNING: SENDER_PASSWORD not configured in .env file!")
    print("   Please edit .env and add your Gmail App Password")
    print("   Get it from: https://myaccount.google.com/apppasswords")

# Try to import optional modules
try:
    from template_manager import TemplateManager
    from email_list_manager import EmailListManager
    from stats_dashboard import StatsDashboard
    from campaign_scheduler import CampaignScheduler
    from smtp_account_manager import SMTPAccountManager
    from bounce_handler import BounceHandler
    from warmup_manager import WarmupManager
    from ab_test_manager import ABTestManager
    from css_injector import CSSInjector
    from spam_checker import SpamChecker
    from email_validator import EmailValidator
    from engagement_tracker import EngagementTracker
    from opt_in_manager import OptInManager
    from compliance_footer import ComplianceFooterGenerator as ComplianceFooter
    from signature_manager import SignatureManager
    from email_forms import EmailFormGenerator as EmailForms
    from tracking import TrackingManager
    from preheader import PreheaderGenerator
    from email_segmenter import EmailSegmenter
    from domain_auth_checker import DomainAuthChecker
    from email_sender import BulkEmailSender
except ImportError as e:
    print(f"Warning: Some modules not available: {e}")
    BulkEmailSender = None

# Ensure directories exist
IMAGES_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

# Error logging
def log_error(message, error=None):
    """Log errors to file and console"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    error_msg = f"[{timestamp}] {message}"
    if error:
        error_msg += f" - {str(error)}"
    print(error_msg)
    try:
        with open(ERROR_LOG_FILE, 'a') as f:
            f.write(error_msg + '\n')
    except:
        pass


class EnhancedWebAppHandler(BaseHTTPRequestHandler):
    """Enhanced Web Application Handler with advanced features."""

    def log_message(self, format, *args):
        print(f"[WebApp] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {args[0]}")

    def send_html(self, html: str, status: int = 200):
        self.send_response(status)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

    def send_json(self, data: dict, status: int = 200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2, default=str).encode())

    def send_error_json(self, message: str, status: int = 400):
        self.send_json({'error': message, 'success': False}, status)

    def get_request_body(self) -> dict:
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            return {}
        body = self.rfile.read(content_length)
        try:
            return json.loads(body.decode())
        except json.JSONDecodeError:
            return {}

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        try:
            if path == '/':
                self.show_main_app()
            elif path == '/api/stats':
                self.api_get_stats()
            elif path == '/api/templates':
                self.api_list_templates()
            elif path.startswith('/api/templates/'):
                self.api_get_template(query)
            elif path == '/api/emails':
                self.api_list_emails()
            elif path == '/api/campaigns':
                self.api_list_campaigns()
            elif path == '/api/accounts':
                self.api_list_accounts()
            elif path == '/api/bounces':
                self.api_list_bounces()
            elif path == '/api/warmup':
                self.api_list_warmup()
            elif path == '/api/ab-tests':
                self.api_list_ab_tests()
            elif path == '/api/images':
                self.api_list_images()
            elif path == '/api/links':
                self.api_list_links()
            elif path == '/api/errors':
                self.api_get_errors(query)
            elif path == '/api/chart-data':
                self.api_get_chart_data(query)
            elif path == '/api/analytics':
                self.api_get_analytics(query)
            elif path == '/api/send-history':
                self.api_get_send_history(query)
            elif path == '/api/senders':
                self.api_list_senders(query)
            elif path == '/api/health':
                self.api_health_check()
            else:
                self.show_main_app()
        except Exception as e:
            log_error(f"GET {path} failed", e)
            self.send_error_json(str(e), 500)

    def do_POST(self):
        path = urlparse(self.path).path
        body = self.get_request_body()

        try:
            # Email sending - Enhanced
            if path == '/api/send/single':
                self.api_send_single(body)
            elif path == '/api/send/bulk':
                self.api_send_bulk(body)
            elif path == '/api/send/multiple':
                self.api_send_multiple(body)
            elif path == '/api/send/test':
                self.api_send_test(body)
            # Templates - Enhanced
            elif path == '/api/templates/create':
                self.api_create_template(body)
            elif path == '/api/templates/update':
                self.api_update_template(body)
            elif path == '/api/templates/delete':
                self.api_delete_template(body)
            elif path == '/api/templates/clone':
                self.api_clone_template(body)
            elif path == '/api/templates/preview':
                self.api_preview_template(body)
            elif path == '/api/templates/customize':
                self.api_customize_template(body)
            elif path == '/api/templates/import-html':
                self.api_import_html(body)
            # Images
            elif path == '/api/images/upload':
                self.api_upload_image(body)
            elif path == '/api/images/delete':
                self.api_delete_image(body)
            # Links
            elif path == '/api/links/add':
                self.api_add_link(body)
            elif path == '/api/links/update':
                self.api_update_link(body)
            elif path == '/api/links/delete':
                self.api_delete_link(body)
            # Email list
            elif path == '/api/emails/add':
                self.api_add_email(body)
            elif path == '/api/emails/delete':
                self.api_delete_email(body)
            elif path == '/api/emails/validate':
                self.api_validate_email(body)
            elif path == '/api/emails/clean':
                self.api_clean_emails(body)
            elif path == '/api/emails/import':
                self.api_import_emails(body)
            elif path == '/api/emails/export':
                self.api_export_emails(body)
            elif path == '/api/emails/dedup':
                self.api_dedup_emails(body)
            # Campaigns
            elif path == '/api/campaigns/schedule':
                self.api_schedule_campaign(body)
            elif path == '/api/campaigns/cancel':
                self.api_cancel_campaign(body)
            # SMTP Accounts
            elif path == '/api/accounts/add':
                self.api_add_account(body)
            elif path == '/api/accounts/delete':
                self.api_delete_account(body)
            # Bounces
            elif path == '/api/bounces/record':
                self.api_record_bounce(body)
            elif path == '/api/bounces/check':
                self.api_check_bounce(body)
            # Warmup
            elif path == '/api/warmup/start':
                self.api_start_warmup(body)
            # A/B Tests
            elif path == '/api/ab-tests/create':
                self.api_create_ab_test(body)
            elif path == '/api/ab-tests/start':
                self.api_start_ab_test(body)
            # Compliance
            elif path == '/api/domain/check':
                self.api_check_domain(body)
            elif path == '/api/spam/check':
                self.api_check_spam(body)
            elif path == '/api/optin/subscribe':
                self.api_optin_subscribe(body)
            elif path == '/api/optin/confirm':
                self.api_optin_confirm(body)
            elif path == '/api/optin/unsubscribe':
                self.api_optin_unsubscribe(body)
            elif path == '/api/footer/generate':
                self.api_generate_footer(body)
            # Tools
            elif path == '/api/css/apply':
                self.api_apply_css(body)
            elif path == '/api/signature/create':
                self.api_create_signature(body)
            elif path == '/api/form/generate':
                self.api_generate_form(body)
            elif path == '/api/preheader/generate':
                self.api_generate_preheader(body)
            elif path == '/api/segment':
                self.api_segment_emails(body)
            # Settings
            elif path == '/api/settings/save':
                self.api_save_settings(body)
            # Senders
            elif path == '/api/senders/add':
                self.api_add_sender(body)
            elif path == '/api/senders/update':
                self.api_update_sender(body)
            elif path == '/api/senders/delete':
                self.api_delete_sender(body)
            elif path == '/api/senders/test':
                self.api_test_sender(body)
            else:
                self.send_error_json('Endpoint not found', 404)
        except Exception as e:
            log_error(f"POST {path} failed", e)
            self.send_error_json(str(e), 500)

    def show_main_app(self):
        from web_html_enhanced import get_complete_html
        self.send_html(get_complete_html())

    def api_health_check(self):
        self.send_json({'status': 'healthy', 'timestamp': datetime.now().isoformat(), 'version': '5.0'})

    def api_get_stats(self):
        try:
            dashboard = StatsDashboard(LOGS_DIR)
            summary = dashboard.get_summary()
        except:
            summary = {'total_campaigns': 0, 'total_sent': 0, 'success_rate': 100}

        email_count = 0
        if EMAIL_LIST_FILE.exists():
            with open(EMAIL_LIST_FILE, 'r') as f:
                email_count = sum(1 for line in f if line.strip() and not line.startswith('#') and '@' in line)

        template_count = 0
        if TEMPLATES_DIR.exists():
            template_count = len(list(TEMPLATES_DIR.glob('*.html')))

        image_count = len(list(IMAGES_DIR.glob('*.png')) + list(IMAGES_DIR.glob('*.jpg')) + list(IMAGES_DIR.glob('*.gif')))

        summary['email_count'] = email_count
        summary['template_count'] = template_count
        summary['image_count'] = image_count
        self.send_json(summary)

    def api_list_templates(self):
        templates = []
        if TEMPLATES_DIR.exists():
            manager = TemplateManager(TEMPLATES_DIR)
            templates = manager.list_templates()
        self.send_json({'templates': templates, 'total': len(templates)})

    def api_get_template(self, query):
        name = query.get('name', [None])[0]
        if not name:
            self.send_error_json('Missing template name')
            return
        manager = TemplateManager(TEMPLATES_DIR)
        template = manager.get_template(name)
        if template:
            self.send_json({'template': template})
        else:
            self.send_error_json('Template not found', 404)

    def api_list_emails(self):
        manager = EmailListManager(EMAIL_LIST_FILE)
        emails = manager.load_emails()
        valid_count = len([e for e in emails if '@' in e])
        self.send_json({'emails': emails, 'total': len(emails), 'valid': valid_count})

    def api_list_campaigns(self):
        try:
            dashboard = StatsDashboard(LOGS_DIR)
            campaigns = dashboard.get_recent_campaigns(limit=50)
        except:
            campaigns = []
        self.send_json({'campaigns': campaigns})

    def api_list_accounts(self):
        try:
            manager = SMTPAccountManager()
            accounts = manager.get_accounts_summary()
            stats = manager.get_usage_stats()
        except:
            accounts = []
            stats = {}
        self.send_json({'accounts': accounts, 'stats': stats})

    def api_list_bounces(self):
        try:
            handler = BounceHandler()
            bounces = handler.get_bounces(limit=50)
            stats = handler.get_bounce_stats()
        except:
            bounces = []
            stats = {'total': 0}
        self.send_json({'bounces': bounces, 'stats': stats})

    def api_list_warmup(self):
        try:
            manager = WarmupManager()
            sessions = manager.get_all_sessions()
        except:
            sessions = []
        self.send_json({'sessions': sessions})

    def api_list_ab_tests(self):
        try:
            manager = ABTestManager()
            tests = manager.get_all_tests()
        except:
            tests = []
        self.send_json({'tests': tests})

    def api_list_images(self):
        images = []
        if IMAGES_DIR.exists():
            for img in IMAGES_DIR.glob('*'):
                if img.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp']:
                    images.append({
                        'name': img.name,
                        'url': f'/images/{img.name}',
                        'size': img.stat().st_size,
                        'modified': datetime.fromtimestamp(img.stat().st_mtime).isoformat()
                    })
        self.send_json({'images': images, 'total': len(images)})

    def api_list_links(self):
        links_file = DATA_DIR / 'tracked_links.json'
        if links_file.exists():
            with open(links_file, 'r') as f:
                links = json.load(f)
        else:
            links = []
        self.send_json({'links': links})

    def api_get_errors(self, query):
        """Get error logs"""
        limit = int(query.get('limit', [50])[0])
        errors = []
        
        if ERROR_LOG_FILE.exists():
            with open(ERROR_LOG_FILE, 'r') as f:
                lines = f.readlines()
                errors = lines[-limit:]
        
        self.send_json({
            'errors': errors,
            'total': len(errors),
            'log_file': str(ERROR_LOG_FILE)
        })

    def api_get_chart_data(self, query):
        """Get data for charts"""
        try:
            dashboard = StatsDashboard(LOGS_DIR)
            summary = dashboard.get_summary()
            campaigns = dashboard.get_recent_campaigns(limit=20)
        except:
            summary = {'total_campaigns': 0, 'total_sent': 0, 'success_rate': 100}
            campaigns = []
        
        # Prepare chart data
        chart_data = {
            'summary': summary,
            'campaigns': campaigns,
            'labels': [c.get('name', f'Campaign {i+1}') for i, c in enumerate(campaigns[:10])],
            'sent_data': [c.get('sent', 0) for c in campaigns[:10]],
            'success_data': [c.get('success_rate', 100) for c in campaigns[:10]],
            'bounce_data': [c.get('bounces', 0) for c in campaigns[:10]]
        }
        
        self.send_json(chart_data)

    def api_get_analytics(self, query):
        """Get comprehensive analytics data"""
        try:
            dashboard = StatsDashboard(LOGS_DIR)
            summary = dashboard.get_summary()
            campaigns = dashboard.get_recent_campaigns(limit=30)
        except:
            summary = {}
            campaigns = []
        
        # Email list stats
        email_count = 0
        if EMAIL_LIST_FILE.exists():
            with open(EMAIL_LIST_FILE, 'r') as f:
                email_count = sum(1 for line in f if line.strip() and not line.startswith('#') and '@' in line)
        
        # Template stats
        template_count = 0
        if TEMPLATES_DIR.exists():
            template_count = len(list(TEMPLATES_DIR.glob('*.html')))
        
        # Bounce stats
        try:
            handler = BounceHandler()
            bounce_stats = handler.get_bounce_stats()
        except:
            bounce_stats = {'total': 0, 'hard_bounces': 0, 'soft_bounces': 0}
        
        analytics = {
            'summary': summary,
            'email_count': email_count,
            'template_count': template_count,
            'bounce_stats': bounce_stats,
            'campaigns': campaigns,
            'daily_sent': [summary.get('total_sent', 0) // 7 for _ in range(7)],  # Mock data
            'days': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        }
        
        self.send_json(analytics)

    # Enhanced Template Methods
    def api_create_template(self, body):
        name = body.get('name')
        html_content = body.get('html')
        subject = body.get('subject')
        if not name or not html_content:
            self.send_error_json('Missing required fields: name, html')
            return
        manager = TemplateManager(TEMPLATES_DIR)
        try:
            manager.create_template(name, html_content, subject)
            self.send_json({'success': True, 'template': name})
        except ValueError as e:
            self.send_error_json(str(e))

    def api_update_template(self, body):
        name = body.get('name')
        html_content = body.get('html')
        subject = body.get('subject')
        if not name:
            self.send_error_json('Missing template name')
            return
        manager = TemplateManager(TEMPLATES_DIR)
        try:
            manager.update_template(name, html_content, subject)
            self.send_json({'success': True})
        except Exception as e:
            self.send_error_json(str(e))

    def api_delete_template(self, body):
        name = body.get('name')
        if not name:
            self.send_error_json('Missing template name')
            return
        manager = TemplateManager(TEMPLATES_DIR)
        if manager.delete_template(name):
            self.send_json({'success': True})
        else:
            self.send_error_json('Template not found', 404)

    def api_clone_template(self, body):
        source = body.get('source')
        new_name = body.get('new_name')
        if not source or not new_name:
            self.send_error_json('Missing required fields')
            return
        manager = TemplateManager(TEMPLATES_DIR)
        try:
            manager.clone_template(source, new_name)
            self.send_json({'success': True})
        except ValueError as e:
            self.send_error_json(str(e))

    def api_preview_template(self, body):
        name = body.get('name')
        if not name:
            self.send_error_json('Missing template name')
            return
        manager = TemplateManager(TEMPLATES_DIR)
        template = manager.get_template(name)
        if template:
            self.send_json({'success': True, 'template': template})
        else:
            self.send_error_json('Template not found', 404)

    def api_customize_template(self, body):
        """Customize template with colors, fonts, content"""
        name = body.get('name')
        colors = body.get('colors', {})
        fonts = body.get('fonts', {})
        content = body.get('content', {})
        
        if not name:
            self.send_error_json('Missing template name')
            return
            
        manager = TemplateManager(TEMPLATES_DIR)
        template = manager.get_template(name)
        
        if not template:
            self.send_error_json('Template not found', 404)
            return
        
        html = template.get('html', '')
        
        # Replace colors
        for old_color, new_color in colors.items():
            html = html.replace(old_color, new_color)
        
        # Replace fonts
        for old_font, new_font in fonts.items():
            html = html.replace(old_font, new_font)
        
        # Replace content placeholders
        for placeholder, replacement in content.items():
            html = html.replace(f'${{{placeholder}}}', replacement)
        
        self.send_json({'success': True, 'html': html})

    def api_import_html(self, body):
        """Import HTML from paste or URL"""
        name = body.get('name')
        html_content = body.get('html')
        subject = body.get('subject')
        
        if not name or not html_content:
            self.send_error_json('Missing required fields: name, html')
            return
        
        manager = TemplateManager(TEMPLATES_DIR)
        try:
            manager.create_template(name, html_content, subject)
            self.send_json({'success': True, 'template': name})
        except ValueError as e:
            self.send_error_json(str(e))

    # Image Methods
    def api_upload_image(self, body):
        """Upload image as base64"""
        name = body.get('name')
        data = body.get('data')  # base64 data
        
        if not name or not data:
            self.send_error_json('Missing name or data')
            return
        
        try:
            # Remove data URL prefix if present
            if ',' in data:
                data = data.split(',')[1]
            
            image_data = base64.b64decode(data)
            image_path = IMAGES_DIR / name
            
            with open(image_path, 'wb') as f:
                f.write(image_data)
            
            self.send_json({
                'success': True,
                'url': f'/images/{name}',
                'name': name
            })
        except Exception as e:
            self.send_error_json(str(e))

    def api_delete_image(self, body):
        name = body.get('name')
        if not name:
            self.send_error_json('Missing image name')
            return
        
        image_path = IMAGES_DIR / name
        if image_path.exists():
            image_path.unlink()
            self.send_json({'success': True})
        else:
            self.send_error_json('Image not found', 404)

    # Link Methods
    def api_add_link(self, body):
        url = body.get('url')
        name = body.get('name')
        tracking_id = body.get('tracking_id')
        
        if not url:
            self.send_error_json('Missing URL')
            return
        
        links_file = DATA_DIR / 'tracked_links.json'
        if links_file.exists():
            with open(links_file, 'r') as f:
                links = json.load(f)
        else:
            links = []
        
        new_link = {
            'id': len(links) + 1,
            'name': name or url,
            'url': url,
            'tracking_id': tracking_id or f'link_{len(links) + 1}',
            'clicks': 0,
            'created': datetime.now().isoformat()
        }
        
        links.append(new_link)
        
        with open(links_file, 'w') as f:
            json.dump(links, f)
        
        self.send_json({'success': True, 'link': new_link})

    def api_update_link(self, body):
        link_id = body.get('id')
        url = body.get('url')
        name = body.get('name')
        
        links_file = DATA_DIR / 'tracked_links.json'
        if not links_file.exists():
            self.send_error_json('No links found')
            return
        
        with open(links_file, 'r') as f:
            links = json.load(f)
        
        for link in links:
            if link['id'] == link_id:
                if url:
                    link['url'] = url
                if name:
                    link['name'] = name
                break
        
        with open(links_file, 'w') as f:
            json.dump(links, f)
        
        self.send_json({'success': True})

    def api_delete_link(self, body):
        link_id = body.get('id')
        
        links_file = DATA_DIR / 'tracked_links.json'
        if not links_file.exists():
            self.send_error_json('No links found')
            return
        
        with open(links_file, 'r') as f:
            links = json.load(f)
        
        links = [l for l in links if l['id'] != link_id]
        
        with open(links_file, 'w') as f:
            json.dump(links, f)
        
        self.send_json({'success': True})

    # Email Sending - Enhanced with Real SMTP
    def api_send_single(self, body):
        """Send single email with real SMTP using .env configuration"""
        to_email = body.get('to')
        subject = body.get('subject')
        template_name = body.get('template')
        content = body.get('content')
        
        # Use .env config by default (can be overridden in request)
        from_email = body.get('from_email', SENDER_EMAIL)
        from_password = body.get('from_password', SENDER_PASSWORD)
        from_name = body.get('from_name', SENDER_NAME)
        smtp_server = body.get('smtp_server', SMTP_SERVER)
        smtp_port = int(body.get('smtp_port', SMTP_PORT))

        if not to_email or not subject:
            self.send_error_json('Missing required fields: to, subject')
            return

        # Validate .env configuration
        if not from_email or not from_password:
            self.send_error_json(
                'Sender credentials not configured. '
                'Please edit .env file and set:\n'
                '  SENDER_EMAIL=your_email@gmail.com\n'
                '  SENDER_PASSWORD=your_app_password\n'
                'Get Gmail App Password: https://myaccount.google.com/apppasswords'
            )
            return

        # Get template content if provided
        html_content = content
        if template_name and not content:
            manager = TemplateManager(TEMPLATES_DIR)
            template = manager.get_template(template_name)
            if template:
                html_content = template.get('html', '')

        if not html_content:
            html_content = '<p>Hello!</p>'

        # Send with real SMTP
        try:
            import smtplib
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText

            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{from_name} <{from_email}>"
            msg['To'] = to_email

            # Add plain text version
            import re
            plain_text = re.sub(r'<[^>]+>', '', html_content)[:500]
            msg.attach(MIMEText(plain_text, 'plain', 'utf-8'))

            # Add HTML version
            msg.attach(MIMEText(html_content, 'html', 'utf-8'))

            # Connect and send using .env credentials
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(from_email, from_password)

            text = msg.as_string()
            server.sendmail(from_email, to_email, text)
            server.quit()

            # Success!
            send_log = {
                'timestamp': datetime.now().isoformat(),
                'to': to_email,
                'from': from_email,
                'subject': subject,
                'status': 'sent',
                'message': 'Email sent successfully via SMTP',
                'template': template_name,
                'smtp_server': smtp_server,
                'source': '.env config'
            }

            self._save_send_history(send_log)

            self.send_json({
                'success': True,
                'status': 'sent',
                'message': 'Email sent successfully using .env SMTP credentials!',
                'to': to_email,
                'subject': subject,
                'from': from_email,
                'method': 'SMTP (.env)'
            })

        except smtplib.SMTPAuthenticationError:
            error_msg = 'SMTP Authentication failed. Check email and password.'
            log_error(f"Send failed - Auth error", error_msg)
            self._save_send_history({
                'timestamp': datetime.now().isoformat(),
                'to': to_email,
                'from': from_email,
                'subject': subject,
                'status': 'failed',
                'message': error_msg,
                'template': template_name
            })
            self.send_error_json(error_msg)
            
        except smtplib.SMTPConnectError as e:
            error_msg = f'SMTP Connection failed: {str(e)}'
            log_error(f"Send failed - Connect error", error_msg)
            self._save_send_history({
                'timestamp': datetime.now().isoformat(),
                'to': to_email,
                'from': from_email,
                'subject': subject,
                'status': 'failed',
                'message': error_msg,
                'template': template_name
            })
            self.send_error_json(error_msg)
            
        except Exception as e:
            error_msg = f'Failed to send: {str(e)}'
            log_error(f"Send failed", e)
            self._save_send_history({
                'timestamp': datetime.now().isoformat(),
                'to': to_email,
                'from': from_email,
                'subject': subject,
                'status': 'failed',
                'message': error_msg,
                'template': template_name
            })
            self.send_error_json(error_msg)

    def api_send_bulk(self, body):
        """Send bulk emails with real SMTP using .env configuration"""
        template = body.get('template')
        subject = body.get('subject')
        
        # Use .env config by default (can be overridden in request)
        from_email = body.get('from_email', SENDER_EMAIL)
        from_password = body.get('from_password', SENDER_PASSWORD)
        from_name = body.get('from_name', SENDER_NAME)
        smtp_server = body.get('smtp_server', SMTP_SERVER)
        smtp_port = int(body.get('smtp_port', SMTP_PORT))
        batch_size = body.get('batch_size', 25)
        delay_min = body.get('delay_min', 1)
        delay_max = body.get('delay_max', 3)

        if not from_email or not from_password:
            self.send_error_json(
                'Sender credentials not configured. '
                'Please edit .env file and set:\n'
                '  SENDER_EMAIL=your_email@gmail.com\n'
                '  SENDER_PASSWORD=your_app_password\n'
                'Get Gmail App Password: https://myaccount.google.com/apppasswords'
            )
            return
        
        # Load email list
        manager = EmailListManager(EMAIL_LIST_FILE)
        emails = manager.load_emails()
        
        if not emails:
            self.send_error_json('No emails in list')
            return
        
        # Get template
        import re
        html_content = '<p>Hello!</p>'
        if template:
            tmpl_manager = TemplateManager(TEMPLATES_DIR)
            tmpl = tmpl_manager.get_template(template)
            if tmpl:
                html_content = tmpl.get('html', '')
        
        sent_count = 0
        failed_count = 0
        results = []
        
        try:
            import smtplib
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText
            import random
            
            # Connect to SMTP server
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(from_email, from_password)
            
            # Send to each email
            for i, email in enumerate(emails[:100]):  # Limit to 100
                try:
                    # Create message
                    msg = MIMEMultipart('alternative')
                    msg['Subject'] = subject
                    msg['From'] = f"{from_name} <{from_email}>"
                    msg['To'] = email
                    
                    # Add plain text
                    plain_text = re.sub(r'<[^>]+>', '', html_content)[:500]
                    msg.attach(MIMEText(plain_text, 'plain', 'utf-8'))
                    
                    # Add HTML
                    msg.attach(MIMEText(html_content, 'html', 'utf-8'))
                    
                    # Send
                    server.sendmail(from_email, email, msg.as_string())
                    sent_count += 1
                    
                    results.append({
                        'email': email,
                        'status': 'sent',
                        'message': 'Sent successfully'
                    })
                    
                    # Save history
                    self._save_send_history({
                        'timestamp': datetime.now().isoformat(),
                        'to': email,
                        'from': from_email,
                        'subject': subject,
                        'status': 'sent',
                        'template': template
                    })
                    
                    # Delay between emails
                    if i < len(emails) - 1:
                        delay = random.uniform(delay_min, delay_max)
                        time.sleep(delay)
                    
                    # Batch delay
                    if (i + 1) % batch_size == 0:
                        print(f"Sent {i + 1} emails, pausing...")
                        
                except Exception as e:
                    failed_count += 1
                    results.append({
                        'email': email,
                        'status': 'failed',
                        'message': str(e)
                    })
                    
                    self._save_send_history({
                        'timestamp': datetime.now().isoformat(),
                        'to': email,
                        'from': from_email,
                        'subject': subject,
                        'status': 'failed',
                        'message': str(e),
                        'template': template
                    })
            
            server.quit()
            
            self.send_json({
                'success': True,
                'status': 'completed',
                'sent': sent_count,
                'failed': failed_count,
                'total': len(emails),
                'results': results[:20],
                'method': 'SMTP'
            })
            
        except smtplib.SMTPAuthenticationError:
            error_msg = 'SMTP Authentication failed. Check email and password.'
            log_error(f"Bulk send failed - Auth error", error_msg)
            self.send_error_json(error_msg)
            
        except Exception as e:
            error_msg = f'Bulk send failed: {str(e)}'
            log_error(f"Bulk send failed", e)
            self.send_error_json(error_msg)

    def api_send_test(self, body):
        """Send test email with REAL SMTP using .env configuration"""
        to = body.get('to')
        template = body.get('template')
        subject = body.get('subject', 'Test Email')
        
        # Use .env config by default (can be overridden in request)
        from_email = body.get('from_email', SENDER_EMAIL)
        from_password = body.get('from_password', SENDER_PASSWORD)
        from_name = body.get('from_name', SENDER_NAME)
        smtp_server = body.get('smtp_server', SMTP_SERVER)
        smtp_port = int(body.get('smtp_port', SMTP_PORT))

        if not to:
            self.send_error_json('Missing recipient email')
            return

        # Validate .env configuration
        if not from_email or not from_password:
            self.send_error_json(
                'Sender credentials not configured. '
                'Please edit .env file and set:\n'
                '  SENDER_EMAIL=your_email@gmail.com\n'
                '  SENDER_PASSWORD=your_app_password\n'
                'Get Gmail App Password: https://myaccount.google.com/apppasswords'
            )
            return

        # Get template content if provided
        html_content = '<p>This is a test email from Email Bot v5.0!</p>'
        if template:
            tmpl_manager = TemplateManager(TEMPLATES_DIR)
            tmpl = tmpl_manager.get_template(template)
            if tmpl:
                html_content = tmpl.get('html', '')

        # Send with REAL SMTP
        try:
            import smtplib
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText
            import re

            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{from_name} <{from_email}>"
            msg['To'] = to

            # Add plain text version
            plain_text = re.sub(r'<[^>]+>', '', html_content)[:500]
            msg.attach(MIMEText(plain_text, 'plain', 'utf-8'))

            # Add HTML version
            msg.attach(MIMEText(html_content, 'html', 'utf-8'))

            # Connect and send
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(from_email, from_password)
            server.sendmail(from_email, to, msg.as_string())
            server.quit()

            self.send_json({
                'success': True,
                'message': 'Test email sent successfully via REAL SMTP!',
                'to': to,
                'from': from_email,
                'subject': subject,
                'method': 'SMTP'
            })

        except smtplib.SMTPAuthenticationError:
            self.send_error_json('SMTP Authentication failed. Check email and password.')
        except smtplib.SMTPConnectError as e:
            self.send_error_json(f'SMTP Connection failed: {str(e)}')
        except Exception as e:
            self.send_error_json(f'Failed to send test: {str(e)}')

    # Other API methods (same as before for brevity)
    def api_list_campaigns(self):
        try:
            dashboard = StatsDashboard(LOGS_DIR)
            campaigns = dashboard.get_recent_campaigns(limit=50)
        except:
            campaigns = []
        self.send_json({'campaigns': campaigns})

    def api_schedule_campaign(self, body):
        required = ['name', 'scheduled_for', 'template', 'subject', 'email_list', 'sender_email']
        for field in required:
            if field not in body:
                self.send_error_json(f'Missing required field: {field}')
                return
        scheduler = CampaignScheduler()
        try:
            scheduled_for = datetime.fromisoformat(body['scheduled_for'])
        except ValueError:
            self.send_error_json('Invalid date format')
            return
        campaign_id = scheduler.schedule_campaign(
            name=body['name'], scheduled_for=scheduled_for, template=body['template'],
            subject=body['subject'], email_list_file=body['email_list'],
            sender_email=body['sender_email'], sender_name=body.get('sender_name', 'Your Company'),
            batch_size=body.get('batch_size', 25)
        )
        self.send_json({'success': True, 'campaign_id': campaign_id})

    def api_cancel_campaign(self, body):
        campaign_id = body.get('campaign_id')
        if not campaign_id:
            self.send_error_json('Missing campaign_id')
            return
        scheduler = CampaignScheduler()
        if scheduler.cancel_campaign(campaign_id):
            self.send_json({'success': True})
        else:
            self.send_error_json('Failed to cancel campaign', 400)

    def api_add_account(self, body):
        required = ['name', 'email', 'password', 'smtp_server']
        for field in required:
            if field not in body:
                self.send_error_json(f'Missing required field: {field}')
                return
        manager = SMTPAccountManager()
        try:
            account_id = manager.add_account(
                name=body['name'], email=body['email'], password=body['password'],
                smtp_server=body['smtp_server'], smtp_port=body.get('smtp_port', 587),
                daily_limit=body.get('daily_limit', 500)
            )
            self.send_json({'success': True, 'account_id': account_id})
        except ValueError as e:
            self.send_error_json(str(e))

    def api_delete_account(self, body):
        account_id = body.get('account_id')
        if not account_id:
            self.send_error_json('Missing account_id')
            return
        manager = SMTPAccountManager()
        if manager.delete_account(account_id):
            self.send_json({'success': True})
        else:
            self.send_error_json('Account not found', 404)

    def api_record_bounce(self, body):
        email = body.get('email')
        if not email:
            self.send_error_json('Missing email')
            return
        handler = BounceHandler()
        bounce_id = handler.record_bounce(email, body.get('message', ''), body.get('bounce_type', 'soft'))
        self.send_json({'success': True, 'bounce_id': bounce_id})

    def api_check_bounce(self, body):
        email = body.get('email')
        if not email:
            self.send_error_json('Missing email')
            return
        handler = BounceHandler()
        is_suppressed = handler.is_suppressed(email)
        self.send_json({'email': email, 'suppressed': is_suppressed})

    def api_start_warmup(self, body):
        email = body.get('email')
        if not email:
            self.send_error_json('Missing email')
            return
        manager = WarmupManager()
        try:
            session_id = manager.start_warmup(email)
            self.send_json({'success': True, 'session_id': session_id})
        except ValueError as e:
            self.send_error_json(str(e))

    def api_create_ab_test(self, body):
        required = ['name', 'email_list', 'variants']
        for field in required:
            if field not in body:
                self.send_error_json(f'Missing required field: {field}')
                return
        manager = ABTestManager()
        test_id = manager.create_test(
            name=body['name'], email_list_file=body['email_list'],
            variants=body['variants'], sample_size_percent=body.get('sample_size', 20)
        )
        self.send_json({'success': True, 'test_id': test_id})

    def api_start_ab_test(self, body):
        test_id = body.get('test_id')
        if not test_id:
            self.send_error_json('Missing test_id')
            return
        manager = ABTestManager()
        if manager.start_test(test_id):
            self.send_json({'success': True})
        else:
            self.send_error_json('Failed to start test', 400)

    def api_check_domain(self, body):
        domain = body.get('domain')
        provider = body.get('provider', 'gmail')
        if not domain:
            self.send_error_json('Missing domain')
            return
        checker = DomainAuthChecker()
        results = checker.check_all(domain, provider)
        self.send_json({'domain': domain, 'results': results})

    def api_check_spam(self, body):
        content = body.get('content', '')
        subject = body.get('subject', '')
        checker = SpamChecker()
        results = checker.check_content(content, subject)
        self.send_json(results)

    def api_optin_subscribe(self, body):
        email = body.get('email')
        if not email:
            self.send_error_json('Missing email')
            return
        manager = OptInManager()
        result = manager.subscribe(email)
        self.send_json(result)

    def api_optin_confirm(self, body):
        token = body.get('token')
        if not token:
            self.send_error_json('Missing token')
            return
        manager = OptInManager()
        result = manager.confirm(token)
        self.send_json(result)

    def api_optin_unsubscribe(self, body):
        email = body.get('email')
        if not email:
            self.send_error_json('Missing email')
            return
        manager = OptInManager()
        result = manager.unsubscribe(email)
        self.send_json(result)

    def api_generate_footer(self, body):
        company_info = body.get('company_info', {})
        unsubscribe_url = body.get('unsubscribe_url', '#')
        footer = ComplianceFooter()
        generated = footer.generate_footer(company_info, unsubscribe_url)
        self.send_json({'footer': generated})

    def api_apply_css(self, body):
        template_name = body.get('template')
        preset = body.get('preset')
        custom_css = body.get('custom_css')
        if not template_name:
            self.send_error_json('Missing template name')
            return
        injector = CSSInjector()
        manager = TemplateManager(TEMPLATES_DIR)
        template = manager.get_template(template_name)
        if not template:
            self.send_error_json('Template not found', 404)
            return
        html_content = template.get('html', '')
        if preset:
            html_content = injector.apply_preset(html_content, preset)
        if custom_css:
            html_content = injector.inject_css(html_content, custom_css)
        self.send_json({'success': True, 'html': html_content})

    def api_create_signature(self, body):
        manager = SignatureManager()
        signature = manager.create_signature(
            name=body.get('name', 'Your Name'),
            title=body.get('title', 'Your Title'),
            company=body.get('company', 'Company'),
            template=body.get('template', 'modern'),
            primary_color=body.get('color', '#667eea')
        )
        self.send_json({'signature': signature})

    def api_generate_form(self, body):
        form_type = body.get('type', 'popup')
        config = body.get('config', {})
        generator = EmailForms()
        form_html = generator.generate_form(form_type, config)
        self.send_json({'form_html': form_html})

    def api_generate_preheader(self, body):
        content = body.get('content')
        method = body.get('method', 'summary')
        if not content:
            self.send_error_json('Missing content')
            return
        generator = PreheaderGenerator()
        preheader = generator.generate(content, method)
        self.send_json({'preheader': preheader})

    def api_segment_emails(self, body):
        criteria = body.get('criteria', 'domain')
        segmenter = EmailSegmenter(EMAIL_LIST_FILE)
        if criteria == 'domain':
            segment = segmenter.segment_by_domain(body.get('value', ''))
        elif criteria == 'engagement':
            segment = segmenter.segment_by_engagement()
        else:
            segment = segmenter.get_all_segments()
        self.send_json({'segment': segment})

    def api_save_settings(self, body):
        env_file = Path(__file__).parent / '.env'
        env_content = f"# Email Bot Configuration\nSMTP_SERVER={body.get('smtp_server', 'smtp.gmail.com')}\nSMTP_PORT={body.get('smtp_port', 587)}\nSENDER_EMAIL={body.get('sender_email', '')}\nSENDER_PASSWORD={body.get('sender_password', '')}\nSENDER_NAME={body.get('sender_name', 'Your Company')}\nDELAY_MIN={body.get('delay_min', 1)}\nDELAY_MAX={body.get('delay_max', 3)}\nBATCH_SIZE={body.get('batch_size', 25)}\n"
        with open(env_file, 'w') as f:
            f.write(env_content)
        self.send_json({'success': True, 'message': 'Settings saved'})

    def _save_send_history(self, send_log):
        """Save send history to file"""
        history_file = LOGS_DIR / 'send_history.json'
        
        history = []
        if history_file.exists():
            try:
                with open(history_file, 'r') as f:
                    history = json.load(f)
            except:
                history = []
        
        history.append(send_log)
        history = history[-1000:]  # Keep last 1000 records
        
        with open(history_file, 'w') as f:
            json.dump(history, f, indent=2)

    def api_get_send_history(self, query):
        """Get send history"""
        limit = int(query.get('limit', [50])[0])
        status_filter = query.get('status', [None])[0]
        
        history_file = LOGS_DIR / 'send_history.json'
        history = []
        
        if history_file.exists():
            with open(history_file, 'r') as f:
                history = json.load(f)
        
        # Filter by status
        if status_filter:
            history = [h for h in history if h.get('status') == status_filter]
        
        # Sort by timestamp descending
        history.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        # Get statistics
        total = len(history)
        sent = len([h for h in history if h.get('status') == 'sent'])
        failed = len([h for h in history if h.get('status') == 'failed'])
        
        self.send_json({
            'history': history[-limit:],
            'total': total,
            'sent': sent,
            'failed': failed,
            'success_rate': round((sent / total * 100) if total > 0 else 0, 2)
        })

    def api_add_sender(self, body):
        """Add new sender email/password"""
        name = body.get('name')
        email = body.get('email')
        password = body.get('password')
        smtp_server = body.get('smtp_server', 'smtp.gmail.com')
        smtp_port = int(body.get('smtp_port', 587))
        is_default = body.get('is_default', False)
        
        if not name or not email or not password:
            self.send_error_json('Missing required fields: name, email, password')
            return
        
        # Load existing senders
        senders_file = DATA_DIR / 'senders.json'
        senders = []
        if senders_file.exists():
            with open(senders_file, 'r') as f:
                senders = json.load(f)
        
        # Check for duplicate email
        for sender in senders:
            if sender.get('email') == email:
                self.send_error_json('Email already exists')
                return
        
        # If default, unset others
        if is_default:
            for sender in senders:
                sender['is_default'] = False
        
        new_sender = {
            'id': len(senders) + 1,
            'name': name,
            'email': email,
            'password': password,  # In production, encrypt this!
            'smtp_server': smtp_server,
            'smtp_port': smtp_port,
            'is_default': is_default or len(senders) == 0,
            'created': datetime.now().isoformat(),
            'status': 'active'
        }
        
        senders.append(new_sender)
        
        with open(senders_file, 'w') as f:
            json.dump(senders, f, indent=2)
        
        self.send_json({'success': True, 'sender': new_sender})

    def api_list_senders(self, query):
        """List all sender accounts"""
        senders_file = DATA_DIR / 'senders.json'
        senders = []
        
        if senders_file.exists():
            with open(senders_file, 'r') as f:
                senders = json.load(f)
        
        # Remove passwords from response for security
        safe_senders = []
        for sender in senders:
            safe_sender = {k: v for k, v in sender.items() if k != 'password'}
            safe_sender['password_set'] = bool(sender.get('password'))
            safe_senders.append(safe_sender)
        
        self.send_json({'senders': safe_senders, 'total': len(safe_senders)})

    def api_update_sender(self, body):
        """Update sender account"""
        sender_id = body.get('id')
        if not sender_id:
            self.send_error_json('Missing sender ID')
            return
        
        senders_file = DATA_DIR / 'senders.json'
        if not senders_file.exists():
            self.send_error_json('No senders found')
            return
        
        with open(senders_file, 'r') as f:
            senders = json.load(f)
        
        for sender in senders:
            if sender.get('id') == sender_id:
                if 'name' in body:
                    sender['name'] = body['name']
                if 'email' in body:
                    sender['email'] = body['email']
                if 'password' in body and body['password']:
                    sender['password'] = body['password']
                if 'smtp_server' in body:
                    sender['smtp_server'] = body['smtp_server']
                if 'smtp_port' in body:
                    sender['smtp_port'] = body['smtp_port']
                if 'status' in body:
                    sender['status'] = body['status']
                if body.get('is_default'):
                    for s in senders:
                        s['is_default'] = False
                    sender['is_default'] = True
                
                with open(senders_file, 'w') as f:
                    json.dump(senders, f, indent=2)
                
                self.send_json({'success': True, 'sender': sender})
                return
        
        self.send_error_json('Sender not found', 404)

    def api_delete_sender(self, body):
        """Delete sender account"""
        sender_id = body.get('id')
        if not sender_id:
            self.send_error_json('Missing sender ID')
            return
        
        senders_file = DATA_DIR / 'senders.json'
        if not senders_file.exists():
            self.send_error_json('No senders found')
            return
        
        with open(senders_file, 'r') as f:
            senders = json.load(f)
        
        senders = [s for s in senders if s.get('id') != sender_id]
        
        with open(senders_file, 'w') as f:
            json.dump(senders, f, indent=2)
        
        self.send_json({'success': True})

    def api_test_sender(self, body):
        """Test sender credentials"""
        email = body.get('email')
        password = body.get('password')
        smtp_server = body.get('smtp_server', 'smtp.gmail.com')
        smtp_port = int(body.get('smtp_port', 587))
        
        if not email or not password:
            self.send_error_json('Missing email or password')
            return
        
        try:
            if EmailSender:
                sender = EmailSender(
                    smtp_server=smtp_server,
                    smtp_port=smtp_port,
                    sender_email=email,
                    sender_password=password,
                    sender_name='Test'
                )
                
                # Try to connect and authenticate
                import smtplib
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
                server.login(email, password)
                server.quit()
                
                self.send_json({
                    'success': True,
                    'message': 'SMTP connection successful',
                    'email': email
                })
            else:
                self.send_json({
                    'success': True,
                    'message': 'Demo mode - credentials accepted',
                    'email': email
                })
        except Exception as e:
            log_error(f"Sender test failed", e)
            self.send_error_json(f'Connection failed: {str(e)}')

    # Email list methods
    def api_add_email(self, body):
        email = body.get('email')
        if not email:
            self.send_error_json('Missing email address')
            return
        manager = EmailListManager(EMAIL_LIST_FILE)
        success, message = manager.add_email(email, body.get('validate', True))
        if success:
            self.send_json({'success': True, 'message': message})
        else:
            self.send_error_json(message)

    def api_delete_email(self, body):
        email = body.get('email')
        if not email:
            self.send_error_json('Missing email address')
            return
        manager = EmailListManager(EMAIL_LIST_FILE)
        success, message = manager.remove_email(email)
        if success:
            self.send_json({'success': True})
        else:
            self.send_error_json(message, 404)

    def api_validate_email(self, body):
        email = body.get('email')
        if not email:
            self.send_error_json('Missing email address')
            return
        validator = EmailValidator()
        result = validator.validate_full(email)
        self.send_json(result)

    def api_clean_emails(self, body):
        manager = EmailListManager(EMAIL_LIST_FILE)
        result = manager.remove_invalid(body.get('check_dns', False))
        self.send_json({'success': True, 'original': result.get('original_count', 0), 'valid': result.get('valid', 0), 'removed_invalid': result.get('removed_invalid', 0)})

    def api_import_emails(self, body):
        file_path = body.get('file')
        column = body.get('column', 'email')
        if not file_path:
            self.send_error_json('Missing file path')
            return
        manager = EmailListManager(EMAIL_LIST_FILE)
        try:
            count = manager.import_csv(Path(file_path), column)
            self.send_json({'success': True, 'imported': count})
        except Exception as e:
            self.send_error_json(str(e))

    def api_export_emails(self, body):
        output_file = body.get('file', 'exported_emails.csv')
        manager = EmailListManager(EMAIL_LIST_FILE)
        try:
            count = manager.export_csv(Path(output_file), body.get('include_validation', False))
            self.send_json({'success': True, 'exported': count})
        except Exception as e:
            self.send_error_json(str(e))

    def api_dedup_emails(self, body):
        manager = EmailListManager(EMAIL_LIST_FILE)
        result = manager.remove_duplicates()
        self.send_json({'success': True, 'original': result.get('original_count', 0), 'unique': result.get('unique_count', 0), 'duplicates_removed': result.get('duplicates_removed', 0)})


def run_web_app(port=8080):
    server = HTTPServer(('0.0.0.0', port), EnhancedWebAppHandler)
    print(f"\n{'='*60}")
    print(f"🌐 Email Bot Web Application v5.0 - Enhanced Edition")
    print(f"{'='*60}")
    print(f"📍 Running at: http://localhost:{port}")
    print(f"📱 Mobile-responsive design")
    print(f"🎨 Advanced template editor")
    print(f"🖼️  Image management")
    print(f"🔗 Link tracking")
    print(f"📧 Enhanced email sending")
    print(f"\n⚠️  Press Ctrl+C to stop")
    print(f"{'='*60}\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
        server.shutdown()


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run_web_app(port)
