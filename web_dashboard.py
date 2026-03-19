"""Web Dashboard - Simple web interface for email bot management."""
import json
from pathlib import Path
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import sys

sys.path.insert(0, str(Path(__file__).parent))

from config import TEMPLATES_DIR
from email_list_manager import EmailListManager
from stats_dashboard import StatsDashboard


class WebDashboardHandler(BaseHTTPRequestHandler):
    """HTTP request handler for web dashboard."""

    def log_message(self, format, *args):
        """Custom logging."""
        print(f"[Web] {datetime.now().strftime('%H:%M:%S')} - {args[0]}")

    def send_html(self, html: str, status: int = 200):
        """Send HTML response."""
        self.send_response(status)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

    def send_json(self, data: dict, status: int = 200):
        """Send JSON response."""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, default=str).encode())

    def do_GET(self):
        """Handle GET requests."""
        path = self.path.split('?')[0]

        if path == '/':
            self.show_dashboard()
        elif path == '/api/stats':
            self.get_stats()
        elif path == '/api/emails':
            self.get_emails()
        elif path == '/api/templates':
            self.get_templates()
        else:
            self.send_html("<h1>404 Not Found</h1>", 404)

    def show_dashboard(self):
        """Show main dashboard."""
        # Get stats
        stats_dashboard = StatsDashboard()
        summary = stats_dashboard.get_summary()
        
        # Get email list stats
        email_list = Path(__file__).parent / 'data' / 'email_list.txt'
        email_count = 0
        if email_list.exists():
            with open(email_list, 'r') as f:
                email_count = sum(1 for line in f if line.strip() and not line.startswith('#') and '@' in line)

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Email Bot Dashboard</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: white; border-radius: 15px; padding: 30px; margin-bottom: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }}
        .header h1 {{ color: #667eea; margin-bottom: 10px; }}
        .header p {{ color: #666; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 20px; }}
        .stat-card {{ background: white; border-radius: 15px; padding: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }}
        .stat-card h3 {{ color: #888; font-size: 14px; margin-bottom: 10px; text-transform: uppercase; }}
        .stat-card .value {{ font-size: 36px; font-weight: bold; color: #667eea; }}
        .stat-card .change {{ color: #28a745; font-size: 14px; margin-top: 5px; }}
        .section {{ background: white; border-radius: 15px; padding: 25px; margin-bottom: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }}
        .section h2 {{ color: #333; margin-bottom: 20px; }}
        .btn {{ display: inline-block; padding: 12px 25px; background: #667eea; color: white; text-decoration: none; border-radius: 8px; font-weight: 600; margin: 5px; }}
        .btn:hover {{ opacity: 0.9; }}
        .btn-secondary {{ background: #6c757d; }}
        .feature-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }}
        .feature {{ padding: 15px; background: #f8f9fa; border-radius: 10px; text-align: center; }}
        .feature-icon {{ font-size: 30px; margin-bottom: 10px; }}
        .refresh-btn {{ background: #28a745; border: none; padding: 10px 20px; color: white; border-radius: 8px; cursor: pointer; font-size: 14px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📧 Email Bot Dashboard</h1>
            <p>Manage your email campaigns from one place</p>
            <button class="refresh-btn" onclick="location.reload()">🔄 Refresh</button>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <h3>Total Campaigns</h3>
                <div class="value">{summary.get('total_campaigns', 0)}</div>
                <div class="change">All time</div>
            </div>
            <div class="stat-card">
                <h3>Emails Sent</h3>
                <div class="value">{summary.get('total_sent', 0):,}</div>
                <div class="change">Total sent</div>
            </div>
            <div class="stat-card">
                <h3>Email List</h3>
                <div class="value">{email_count:,}</div>
                <div class="change">Subscribers</div>
            </div>
            <div class="stat-card">
                <h3>Success Rate</h3>
                <div class="value">{summary.get('success_rate', 0):.1f}%</div>
                <div class="change">Average</div>
            </div>
        </div>

        <div class="section">
            <h2>🚀 Quick Actions</h2>
            <div>
                <a href="/send" class="btn">📤 Send Email</a>
                <a href="/templates" class="btn">🎨 Templates</a>
                <a href="/list" class="btn">📋 Email List</a>
                <a href="/analytics" class="btn">📊 Analytics</a>
                <a href="/settings" class="btn">⚙️ Settings</a>
            </div>
        </div>

        <div class="section">
            <h2>✨ Features</h2>
            <div class="feature-grid">
                <div class="feature">
                    <div class="feature-icon">📧</div>
                    <strong>Bulk Sending</strong>
                    <p>Send 10,000+ emails</p>
                </div>
                <div class="feature">
                    <div class="feature-icon">🎨</div>
                    <strong>Templates</strong>
                    <p>20+ professional designs</p>
                </div>
                <div class="feature">
                    <div class="feature-icon">📊</div>
                    <strong>Analytics</strong>
                    <p>Track opens & clicks</p>
                </div>
                <div class="feature">
                    <div class="feature-icon">✅</div>
                    <strong>Compliance</strong>
                    <p>GDPR & CAN-SPAM</p>
                </div>
                <div class="feature">
                    <div class="feature-icon">🔐</div>
                    <strong>Double Opt-In</strong>
                    <p>Verified subscribers</p>
                </div>
                <div class="feature">
                    <div class="feature-icon">📱</div>
                    <strong>Forms</strong>
                    <p>Popup & inline forms</p>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>📝 Recent Activity</h2>
            <p style="color: #666;">No recent activity</p>
        </div>

        <div class="section">
            <h2>🔗 API Endpoints</h2>
            <div style="background: #f8f9fa; padding: 15px; border-radius: 10px; font-family: monospace;">
                <div>GET /api/stats - Get statistics</div>
                <div>GET /api/emails - Get email list</div>
                <div>GET /api/templates - Get templates</div>
                <div>POST /api/send - Send email</div>
            </div>
        </div>
    </div>

    <script>
        // Auto-refresh stats every 30 seconds
        setInterval(() => {{
            fetch('/api/stats')
                .then(r => r.json())
                .then(data => console.log('Stats updated:', data));
        }}, 30000);
    </script>
</body>
</html>"""
        
        self.send_html(html)

    def get_stats(self):
        """Get statistics as JSON."""
        stats_dashboard = StatsDashboard()
        summary = stats_dashboard.get_summary()
        self.send_json(summary)

    def get_emails(self):
        """Get email list."""
        email_list = Path(__file__).parent / 'data' / 'email_list.txt'
        emails = []
        
        if email_list.exists():
            with open(email_list, 'r') as f:
                emails = [line.strip() for line in f if line.strip() and not line.startswith('#') and '@' in line]
        
        self.send_json({'emails': emails, 'total': len(emails)})

    def get_templates(self):
        """Get available templates."""
        templates = []
        
        if TEMPLATES_DIR.exists():
            for f in TEMPLATES_DIR.glob('*.html'):
                templates.append({
                    'name': f.stem,
                    'file': f.name
                })
        
        self.send_json({'templates': templates})


def run_dashboard(port: int = 8000):
    """Run the web dashboard."""
    server = HTTPServer(('0.0.0.0', port), WebDashboardHandler)
    print(f"🌐 Web Dashboard running at http://localhost:{port}")
    print(f"📊 Dashboard: http://localhost:{port}/")
    print(f"📈 API Stats: http://localhost:{port}/api/stats")
    print(f"📧 API Emails: http://localhost:{port}/api/emails")
    print("\nPress Ctrl+C to stop")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Shutting down dashboard...")
        server.shutdown()


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    run_dashboard(port)
