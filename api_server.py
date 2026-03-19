"""REST API Server - HTTP API for email bot integrations."""
import json
import asyncio
import threading
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import TEMPLATES_DIR, EMAIL_LIST_FILE, LOGS_DIR
from template_engine import EmailTemplate
from email_list_manager import EmailListManager
from stats_dashboard import StatsDashboard
from campaign_scheduler import CampaignScheduler
from smtp_account_manager import SMTPAccountManager
from bounce_handler import BounceHandler
from warmup_manager import WarmupManager
from ab_test_manager import ABTestManager
from template_manager import TemplateManager
from css_injector import CSSInjector
from spam_checker import SpamChecker
from email_validator import EmailValidator


class EmailBotAPIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the Email Bot API."""

    # Shared state
    api_server = None

    def log_message(self, format, *args):
        """Override to customize logging."""
        print(f"[API] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {args[0]}")

    def send_json_response(self, data: dict, status: int = 200):
        """Send JSON response."""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2, default=str).encode())

    def send_error_response(self, message: str, status: int = 400):
        """Send error response."""
        self.send_json_response({'error': message}, status)

    def get_request_body(self) -> dict:
        """Parse JSON request body."""
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            return {}

        body = self.rfile.read(content_length)
        try:
            return json.loads(body.decode())
        except json.JSONDecodeError:
            return {}

    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

    def do_GET(self):
        """Handle GET requests."""
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        # Route handling
        routes = {
            '/': self.handle_root,
            '/api/templates': self.handle_templates_list,
            '/api/templates/': self.handle_template_detail,
            '/api/emails': self.handle_emails_list,
            '/api/emails/validate': self.handle_email_validate,
            '/api/campaigns': self.handle_campaigns_list,
            '/api/campaigns/scheduled': self.handle_scheduled_campaigns,
            '/api/stats': self.handle_stats,
            '/api/stats/dashboard': self.handle_dashboard,
            '/api/accounts': self.handle_accounts_list,
            '/api/accounts/': self.handle_account_detail,
            '/api/bounces': self.handle_bounces,
            '/api/bounces/suppression': self.handle_suppression_list,
            '/api/warmup': self.handle_warmup,
            '/api/warmup/': self.handle_warmup_detail,
            '/api/ab-tests': self.handle_ab_tests,
            '/api/ab-tests/': self.handle_ab_test_detail,
            '/api/spam/check': self.handle_spam_check,
            '/api/css/presets': self.handle_css_presets,
            '/api/health': self.handle_health,
        }

        handler = routes.get(path)
        if handler:
            handler(query)
        elif path.startswith('/api/templates/'):
            self.handle_template_detail(query)
        elif path.startswith('/api/accounts/'):
            self.handle_account_detail(query)
        elif path.startswith('/api/warmup/'):
            self.handle_warmup_detail(query)
        elif path.startswith('/api/ab-tests/'):
            self.handle_ab_test_detail(query)
        else:
            self.send_error_response('Not found', 404)

    def do_POST(self):
        """Handle POST requests."""
        parsed = urlparse(self.path)
        path = parsed.path
        body = self.get_request_body()

        routes = {
            '/api/send': self.handle_send_email,
            '/api/send/bulk': self.handle_send_bulk,
            '/api/templates': self.handle_template_create,
            '/api/templates/clone': self.handle_template_clone,
            '/api/emails': self.handle_email_add,
            '/api/emails/import': self.handle_email_import,
            '/api/emails/clean': self.handle_email_clean,
            '/api/campaigns/schedule': self.handle_schedule_campaign,
            '/api/accounts': self.handle_account_add,
            '/api/bounces/record': self.handle_bounce_record,
            '/api/bounces/check': self.handle_bounce_check,
            '/api/warmup/start': self.handle_warmup_start,
            '/api/ab-tests': self.handle_ab_test_create,
            '/api/ab-tests/start': self.handle_ab_test_start,
            '/api/css/apply': self.handle_css_apply,
        }

        handler = routes.get(path)
        if handler:
            handler(body)
        else:
            self.send_error_response('Not found', 404)

    def do_DELETE(self):
        """Handle DELETE requests."""
        parsed = urlparse(self.path)
        path = parsed.path

        if path.startswith('/api/templates/'):
            self.handle_template_delete({'name': path.split('/')[-1]})
        elif path.startswith('/api/emails/'):
            self.handle_email_delete({'email': path.split('/')[-1]})
        elif path.startswith('/api/accounts/'):
            self.handle_account_delete({'id': path.split('/')[-1]})
        else:
            self.send_error_response('Not found', 404)

    # === Root & Health ===

    def handle_root(self, query=None):
        """API root endpoint."""
        self.send_json_response({
            'name': 'Email Bot API',
            'version': '2.0',
            'endpoints': {
                'GET /api/templates': 'List email templates',
                'GET /api/templates/<name>': 'Get template details',
                'POST /api/templates': 'Create template',
                'POST /api/templates/clone': 'Clone template',
                'DELETE /api/templates/<name>': 'Delete template',
                'GET /api/emails': 'List emails',
                'POST /api/emails': 'Add email',
                'POST /api/emails/validate': 'Validate email',
                'POST /api/emails/import': 'Import emails from CSV',
                'POST /api/emails/clean': 'Clean invalid emails',
                'GET /api/campaigns': 'List campaigns',
                'GET /api/campaigns/scheduled': 'List scheduled campaigns',
                'POST /api/campaigns/schedule': 'Schedule campaign',
                'POST /api/send': 'Send single email',
                'POST /api/send/bulk': 'Send bulk emails',
                'GET /api/stats': 'Get statistics',
                'GET /api/stats/dashboard': 'Get dashboard data',
                'GET /api/accounts': 'List SMTP accounts',
                'POST /api/accounts': 'Add SMTP account',
                'GET /api/bounces': 'List bounces',
                'GET /api/bounces/suppression': 'Get suppression list',
                'POST /api/bounces/record': 'Record bounce',
                'POST /api/bounces/check': 'Check if email suppressed',
                'GET /api/warmup': 'List warmup sessions',
                'POST /api/warmup/start': 'Start warmup',
                'GET /api/ab-tests': 'List A/B tests',
                'POST /api/ab-tests': 'Create A/B test',
                'GET /api/css/presets': 'List CSS presets',
                'POST /api/css/apply': 'Apply CSS to template',
                'GET /api/spam/check': 'Check spam score',
                'GET /api/health': 'Health check',
            }
        })

    def handle_health(self, query=None):
        """Health check endpoint."""
        self.send_json_response({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '2.0'
        })

    # === Templates ===

    def handle_templates_list(self, query=None):
        """List all templates."""
        manager = TemplateManager(TEMPLATES_DIR)
        templates = manager.list_templates()
        self.send_json_response({'templates': templates})

    def handle_template_detail(self, query=None):
        """Get template details."""
        path = urlparse(self.path).path
        name = path.split('/')[-1]

        manager = TemplateManager(TEMPLATES_DIR)
        template = manager.get_template(name)

        if template:
            self.send_json_response({'template': template})
        else:
            self.send_error_response(f'Template not found: {name}', 404)

    def handle_template_create(self, body: dict):
        """Create a new template."""
        name = body.get('name')
        html = body.get('html')
        subject = body.get('subject')

        if not name or not html:
            self.send_error_response('Missing required fields: name, html')
            return

        manager = TemplateManager(TEMPLATES_DIR)
        try:
            manager.create_template(name, html, subject)
            self.send_json_response({'success': True, 'template': name})
        except ValueError as e:
            self.send_error_response(str(e))

    def handle_template_clone(self, body: dict):
        """Clone a template."""
        source = body.get('source')
        new_name = body.get('name')
        new_subject = body.get('subject')

        if not source or not new_name:
            self.send_error_response('Missing required fields: source, name')
            return

        manager = TemplateManager(TEMPLATES_DIR)
        try:
            manager.clone_template(source, new_name, new_subject)
            self.send_json_response({'success': True, 'template': new_name})
        except ValueError as e:
            self.send_error_response(str(e))

    def handle_template_delete(self, body: dict):
        """Delete a template."""
        name = body.get('name')
        if not name:
            path = urlparse(self.path).path
            name = path.split('/')[-1]

        manager = TemplateManager(TEMPLATES_DIR)
        if manager.delete_template(name):
            self.send_json_response({'success': True})
        else:
            self.send_error_response(f'Template not found: {name}', 404)

    # === Email List ===

    def handle_emails_list(self, query=None):
        """List emails."""
        manager = EmailListManager(EMAIL_LIST_FILE)
        emails = manager.load_emails()

        limit = int(query.get('limit', [100])[0])
        emails = emails[:limit]

        self.send_json_response({
            'emails': emails,
            'total': len(emails),
            'showing': len(emails)
        })

    def handle_email_add(self, body: dict):
        """Add email to list."""
        email = body.get('email')
        validate = body.get('validate', True)

        if not email:
            self.send_error_response('Missing required field: email')
            return

        manager = EmailListManager(EMAIL_LIST_FILE)
        success, message = manager.add_email(email, validate)

        if success:
            self.send_json_response({'success': True, 'message': message})
        else:
            self.send_error_response(message, 400)

    def handle_email_delete(self, body: dict):
        """Remove email from list."""
        email = body.get('email')
        if not email:
            path = urlparse(self.path).path
            email = path.split('/')[-1]

        manager = EmailListManager(EMAIL_LIST_FILE)
        success, message = manager.remove_email(email)

        if success:
            self.send_json_response({'success': True})
        else:
            self.send_error_response(message, 404)

    def handle_email_validate(self, body: dict):
        """Validate an email address."""
        email = body.get('email')
        if not email:
            # Try from query string
            parsed = urlparse(self.path)
            query = parse_qs(parsed.query)
            email = query.get('email', [None])[0]

        if not email:
            self.send_error_response('Missing required field: email')
            return

        validator = EmailValidator()
        result = validator.validate_full(email)
        self.send_json_response(result)

    def handle_email_import(self, body: dict):
        """Import emails from CSV."""
        file_path = body.get('file')
        column = body.get('column', 'email')

        if not file_path:
            self.send_error_response('Missing required field: file')
            return

        manager = EmailListManager(EMAIL_LIST_FILE)
        try:
            count = manager.import_csv(Path(file_path), column)
            self.send_json_response({'success': True, 'imported': count})
        except Exception as e:
            self.send_error_response(str(e))

    def handle_email_clean(self, body: dict):
        """Clean invalid emails from list."""
        check_dns = body.get('check_dns', False)

        manager = EmailListManager(EMAIL_LIST_FILE)
        result = manager.remove_invalid(check_dns)

        self.send_json_response({
            'success': True,
            'original': result['original_count'],
            'valid': result['valid'],
            'removed_invalid': result['removed_invalid'],
            'removed_risky': result['removed_risky']
        })

    # === Campaigns ===

    def handle_campaigns_list(self, query=None):
        """List campaigns (from logs)."""
        dashboard = StatsDashboard(LOGS_DIR)
        campaigns = dashboard.get_recent_campaigns(limit=20)
        self.send_json_response({'campaigns': campaigns})

    def handle_scheduled_campaigns(self, query=None):
        """List scheduled campaigns."""
        scheduler = CampaignScheduler()
        status = query.get('status', [None])[0]
        campaigns = scheduler.get_all_campaigns(status)
        self.send_json_response({'campaigns': campaigns})

    def handle_schedule_campaign(self, body: dict):
        """Schedule a campaign."""
        required = ['name', 'scheduled_for', 'template', 'subject', 'email_list', 'sender_email']
        for field in required:
            if field not in body:
                self.send_error_response(f'Missing required field: {field}')
                return

        scheduler = CampaignScheduler()

        # Parse scheduled_for
        try:
            scheduled_for = datetime.fromisoformat(body['scheduled_for'])
        except ValueError:
            self.send_error_response('Invalid date format for scheduled_for')
            return

        campaign_id = scheduler.schedule_campaign(
            name=body['name'],
            scheduled_for=scheduled_for,
            template=body['template'],
            subject=body['subject'],
            email_list_file=body['email_list'],
            sender_email=body['sender_email'],
            sender_name=body.get('sender_name', 'Your Company'),
            batch_size=body.get('batch_size', 25),
            delay_min=body.get('delay_min', 1.0),
            delay_max=body.get('delay_max', 3.0),
            batch_delay=body.get('batch_delay', 30)
        )

        self.send_json_response({
            'success': True,
            'campaign_id': campaign_id,
            'scheduled_for': scheduled_for.isoformat()
        })

    def handle_send_email(self, body: dict):
        """Send single email (placeholder - would integrate with email_sender)."""
        # This would integrate with the actual email sender
        self.send_json_response({
            'success': True,
            'message': 'Email queued for sending',
            'to': body.get('to'),
            'template': body.get('template')
        })

    def handle_send_bulk(self, body: dict):
        """Send bulk emails (placeholder)."""
        self.send_json_response({
            'success': True,
            'message': 'Bulk send initiated',
            'template': body.get('template'),
            'estimated_count': body.get('count', 0)
        })

    # === Statistics ===

    def handle_stats(self, query=None):
        """Get overall statistics."""
        dashboard = StatsDashboard(LOGS_DIR)
        summary = dashboard.get_summary()

        scheduler = CampaignScheduler()
        scheduler_stats = scheduler.get_statistics()

        bounce_handler = BounceHandler()
        bounce_stats = bounce_handler.get_bounce_stats()

        self.send_json_response({
            'campaigns': summary,
            'scheduled': scheduler_stats,
            'bounces': bounce_stats
        })

    def handle_dashboard(self, query=None):
        """Get dashboard data."""
        dashboard = StatsDashboard(LOGS_DIR)
        summary = dashboard.get_summary()
        recent = dashboard.get_recent_campaigns(limit=10)

        self.send_json_response({
            'summary': summary,
            'recent_campaigns': recent
        })

    # === SMTP Accounts ===

    def handle_accounts_list(self, query=None):
        """List SMTP accounts."""
        manager = SMTPAccountManager()
        accounts = manager.get_accounts_summary()
        stats = manager.get_usage_stats()

        self.send_json_response({
            'accounts': accounts,
            'stats': stats
        })

    def handle_account_detail(self, query=None):
        """Get account details."""
        path = urlparse(self.path).path
        try:
            account_id = int(path.split('/')[-1])
        except ValueError:
            self.send_error_response('Invalid account ID')
            return

        manager = SMTPAccountManager()
        account = manager.get_account(account_id)

        if account:
            self.send_json_response({'account': account.to_safe_dict()})
        else:
            self.send_error_response(f'Account not found: {account_id}', 404)

    def handle_account_add(self, body: dict):
        """Add SMTP account."""
        required = ['name', 'email', 'password', 'smtp_server']
        for field in required:
            if field not in body:
                self.send_error_response(f'Missing required field: {field}')
                return

        manager = SMTPAccountManager()
        try:
            account_id = manager.add_account(
                name=body['name'],
                email=body['email'],
                password=body['password'],
                smtp_server=body['smtp_server'],
                smtp_port=body.get('smtp_port', 587),
                sender_name=body.get('sender_name'),
                daily_limit=body.get('daily_limit', 500)
            )
            self.send_json_response({'success': True, 'account_id': account_id})
        except ValueError as e:
            self.send_error_response(str(e))

    def handle_account_delete(self, body: dict):
        """Delete SMTP account."""
        path = urlparse(self.path).path
        try:
            account_id = int(path.split('/')[-1])
        except ValueError:
            self.send_error_response('Invalid account ID')
            return

        manager = SMTPAccountManager()
        if manager.delete_account(account_id):
            self.send_json_response({'success': True})
        else:
            self.send_error_response(f'Account not found: {account_id}', 404)

    # === Bounces ===

    def handle_bounces(self, query=None):
        """List bounces."""
        handler = BounceHandler()
        limit = int(query.get('limit', [50])[0])
        bounces = handler.get_bounces(limit=limit)
        stats = handler.get_bounce_stats()

        self.send_json_response({
            'bounces': bounces,
            'stats': stats
        })

    def handle_suppression_list(self, query=None):
        """Get suppression list."""
        handler = BounceHandler()
        limit = int(query.get('limit', [100])[0])
        suppressions = handler.get_suppression_list(limit=limit)

        self.send_json_response({'suppressions': suppressions})

    def handle_bounce_record(self, body: dict):
        """Record a bounce."""
        email = body.get('email')
        message = body.get('message', '')

        if not email:
            self.send_error_response('Missing required field: email')
            return

        handler = BounceHandler()
        bounce_id = handler.record_bounce(email, message)

        self.send_json_response({'success': True, 'bounce_id': bounce_id})

    def handle_bounce_check(self, body: dict):
        """Check if email is suppressed."""
        email = body.get('email')
        if not email:
            self.send_error_response('Missing required field: email')
            return

        handler = BounceHandler()
        is_suppressed = handler.is_suppressed(email)

        self.send_json_response({
            'email': email,
            'suppressed': is_suppressed
        })

    # === Warmup ===

    def handle_warmup(self, query=None):
        """List warmup sessions."""
        manager = WarmupManager()
        sessions = manager.get_all_sessions()

        self.send_json_response({'sessions': sessions})

    def handle_warmup_detail(self, query=None):
        """Get warmup session details."""
        path = urlparse(self.path).path
        try:
            session_id = int(path.split('/')[-1])
        except ValueError:
            self.send_error_response('Invalid session ID')
            return

        manager = WarmupManager()
        settings = manager.get_warmup_settings(session_id)

        self.send_json_response(settings)

    def handle_warmup_start(self, body: dict):
        """Start warmup session."""
        email = body.get('email')

        if not email:
            self.send_error_response('Missing required field: email')
            return

        manager = WarmupManager()
        try:
            session_id = manager.start_warmup(email)
            self.send_json_response({
                'success': True,
                'session_id': session_id
            })
        except ValueError as e:
            self.send_error_response(str(e))

    # === A/B Tests ===

    def handle_ab_tests(self, query=None):
        """List A/B tests."""
        manager = ABTestManager()
        status = query.get('status', [None])[0]
        tests = manager.get_all_tests(status)

        self.send_json_response({'tests': tests})

    def handle_ab_test_detail(self, query=None):
        """Get A/B test details."""
        path = urlparse(self.path).path
        try:
            test_id = int(path.split('/')[-1])
        except ValueError:
            self.send_error_response('Invalid test ID')
            return

        manager = ABTestManager()
        results = manager.get_test_results(test_id)

        self.send_json_response(results)

    def handle_ab_test_create(self, body: dict):
        """Create A/B test."""
        required = ['name', 'email_list', 'variants']
        for field in required:
            if field not in body:
                self.send_error_response(f'Missing required field: {field}')
                return

        manager = ABTestManager()
        test_id = manager.create_test(
            name=body['name'],
            email_list_file=body['email_list'],
            variants=body['variants'],
            description=body.get('description'),
            sample_size_percent=body.get('sample_size', 20),
            winner_criterion=body.get('criterion', 'open_rate')
        )

        self.send_json_response({
            'success': True,
            'test_id': test_id
        })

    def handle_ab_test_start(self, body: dict):
        """Start A/B test."""
        test_id = body.get('test_id')

        if not test_id:
            self.send_error_response('Missing required field: test_id')
            return

        manager = ABTestManager()
        if manager.start_test(test_id):
            self.send_json_response({'success': True})
        else:
            self.send_error_response('Failed to start test')

    # === CSS ===

    def handle_css_presets(self, query=None):
        """List CSS presets."""
        injector = CSSInjector()
        presets = injector.list_presets()
        custom = injector.list_custom_presets()

        self.send_json_response({
            'built_in': presets,
            'custom': custom
        })

    def handle_css_apply(self, body: dict):
        """Apply CSS to template."""
        template = body.get('template')
        preset = body.get('preset')
        custom_css = body.get('css')

        if not template:
            self.send_error_response('Missing required field: template')
            return

        manager = TemplateManager(TEMPLATES_DIR)
        injector = CSSInjector()

        template_data = manager.get_template(template)
        if not template_data:
            self.send_error_response(f'Template not found: {template}', 404)
            return

        if preset:
            css = injector.get_preset(preset)
            if not css:
                self.send_error_response(f'Preset not found: {preset}', 404)
                return
        elif custom_css:
            css = custom_css
        else:
            self.send_error_response('Missing preset or css')
            return

        result = injector.inject_css(template_data['html'], css)

        self.send_json_response({
            'success': True,
            'html': result
        })

    # === Spam Check ===

    def handle_spam_check(self, query=None):
        """Check spam score."""
        parsed = urlparse(self.path)
        query_params = parse_qs(parsed.query)

        subject = query_params.get('subject', [''])[0]
        template = query_params.get('template', [None])[0]

        if not subject and not template:
            self.send_error_response('Missing subject or template parameter')
            return

        checker = SpamChecker()

        if template:
            manager = TemplateManager(TEMPLATES_DIR)
            template_data = manager.get_template(template)
            if template_data:
                subject = subject or template_data['subject']
                html = template_data['html']
            else:
                self.send_error_response(f'Template not found: {template}', 404)
                return
        else:
            html = '<html><body><p>Test content</p></body></html>'

        result = checker.check_full(subject, html)
        self.send_json_response(result)


class EmailBotAPIServer:
    """REST API Server for Email Bot."""

    def __init__(self, host: str = '0.0.0.0', port: int = 8080):
        self.host = host
        self.port = port
        self.server = None
        self._thread = None

    def start(self, blocking: bool = True):
        """Start the API server."""
        EmailBotAPIHandler.api_server = self

        self.server = HTTPServer((self.host, self.port), EmailBotAPIHandler)

        print(f"\n{'='*60}")
        print(f"🚀 Email Bot API Server")
        print(f"{'='*60}")
        print(f"  Host: {self.host}")
        print(f"  Port: {self.port}")
        print(f"  URL: http://{self.host}:{self.port}")
        print(f"  API: http://{self.host}:{self.port}/api")
        print(f"{'='*60}")
        print(f"\nPress Ctrl+C to stop\n")

        if blocking:
            try:
                self.server.serve_forever()
            except KeyboardInterrupt:
                self.stop()
        else:
            self._thread = threading.Thread(target=self.server.serve_forever)
            self._thread.daemon = True
            self._thread.start()

    def stop(self):
        """Stop the API server."""
        if self.server:
            print("\nStopping API server...")
            self.server.shutdown()
            print("API server stopped")


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Email Bot REST API Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8080, help='Port to listen on')

    args = parser.parse_args()

    server = EmailBotAPIServer(host=args.host, port=args.port)
    server.start()


if __name__ == '__main__':
    main()
