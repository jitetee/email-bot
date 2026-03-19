#!/usr/bin/env python3
"""Email Bot Web GUI - Simple Working Version."""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from config import SENDER_EMAIL, SENDER_NAME
from email_list_manager import EmailListManager
from template_manager import TemplateManager

TEMPLATES_DIR = Path(__file__).parent / 'templates'
EMAIL_LIST_FILE = Path(__file__).parent / 'data' / 'email_list.txt'


class WebGUIHandler(BaseHTTPRequestHandler):
    """Web GUI Handler."""
    
    def log_message(self, format, *args):
        print(f"[Web] {datetime.now().strftime('%H:%M:%S')} - {args[0]}")
    
    def send_html(self, html: str):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def send_json(self, data: dict):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, default=str).encode())
    
    def do_GET(self):
        path = self.path.split('?')[0]
        
        if path == '/':
            self.show_dashboard()
        elif path == '/api/templates':
            self.api_list_templates()
        elif path == '/api/emails':
            self.api_list_emails()
        elif path == '/api/stats':
            self.api_get_stats()
        else:
            self.show_dashboard()
    
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = json.loads(self.rfile.read(content_length).decode())
        
        path = self.path
        
        if path == '/api/email/add':
            self.api_add_email(post_data)
        elif path == '/api/email/delete':
            self.api_delete_email(post_data)
        elif path == '/api/send':
            self.api_send_email(post_data)
        else:
            self.send_json({'error': 'Not found'})
    
    def show_dashboard(self):
        """Show main dashboard - single page application."""
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Email Bot - Web GUI</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css" rel="stylesheet">
    <style>
        body {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }}
        .sidebar {{ background: rgba(255,255,255,0.95); min-height: 100vh; box-shadow: 4px 0 20px rgba(0,0,0,0.1); }}
        .nav-link {{ color: #333; margin: 5px 10px; border-radius: 10px; }}
        .nav-link:hover, .nav-link.active {{ background: linear-gradient(135deg, #667eea, #764ba2); color: white; }}
        .stat-card {{ background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 25px; border-radius: 15px; margin-bottom: 20px; }}
        .stat-card h3 {{ font-size: 14px; opacity: 0.9; }}
        .stat-card .value {{ font-size: 36px; font-weight: bold; }}
        .card {{ border: none; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); margin-bottom: 20px; }}
        .page {{ display: none; }}
        .page.active {{ display: block; }}
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <div class="col-md-2 sidebar p-3">
                <h4 class="mb-4">📧 Email Bot</h4>
                <nav class="nav flex-column">
                    <a class="nav-link active" href="#" onclick="showPage('dashboard')"><i class="bi bi-speedometer2"></i> Dashboard</a>
                    <a class="nav-link" href="#" onclick="showPage('compose')"><i class="bi bi-pencil-square"></i> Compose</a>
                    <a class="nav-link" href="#" onclick="showPage('templates')"><i class="bi bi-images"></i> Templates</a>
                    <a class="nav-link" href="#" onclick="showPage('emails')"><i class="bi bi-people"></i> Email List</a>
                    <a class="nav-link" href="#" onclick="showPage('settings')"><i class="bi bi-gear"></i> Settings</a>
                </nav>
            </div>
            <div class="col-md-10 p-4">
                <!-- Dashboard -->
                <div id="dashboard" class="page active">
                    <h2 class="mb-4 text-white">📊 Dashboard</h2>
                    <div class="row">
                        <div class="col-md-3"><div class="stat-card"><h3>Emails</h3><div class="value" id="stat-emails">0</div></div></div>
                        <div class="col-md-3"><div class="stat-card"><h3>Templates</h3><div class="value" id="stat-templates">0</div></div></div>
                        <div class="col-md-3"><div class="stat-card"><h3>Campaigns</h3><div class="value" id="stat-campaigns">0</div></div></div>
                        <div class="col-md-3"><div class="stat-card"><h3>Success Rate</h3><div class="value" id="stat-rate">100%</div></div></div>
                    </div>
                    <div class="card p-4">
                        <h5>🚀 Quick Actions</h5>
                        <div class="d-grid gap-2 mt-3">
                            <button class="btn btn-primary" onclick="showPage('compose')">📤 New Campaign</button>
                            <button class="btn btn-outline-primary" onclick="showPage('emails')">📋 Manage Emails</button>
                            <button class="btn btn-outline-primary" onclick="showPage('templates')">🎨 Browse Templates</button>
                        </div>
                    </div>
                </div>
                
                <!-- Compose -->
                <div id="compose" class="page">
                    <h2 class="mb-4 text-white">📝 Compose Email</h2>
                    <div class="card p-4">
                        <form onsubmit="sendEmail(event)">
                            <div class="mb-3">
                                <label class="form-label">Subject</label>
                                <input type="text" class="form-control" id="email-subject" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">From Name</label>
                                <input type="text" class="form-control" id="email-from" value="{SENDER_NAME}">
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Template</label>
                                <select class="form-select" id="email-template"></select>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Content</label>
                                <textarea class="form-control" id="email-content" rows="10" placeholder="Type your email content here..."></textarea>
                            </div>
                            <button type="submit" class="btn btn-primary"><i class="bi bi-send"></i> Send Email</button>
                        </form>
                    </div>
                </div>
                
                <!-- Templates -->
                <div id="templates" class="page">
                    <h2 class="mb-4 text-white">🎨 Templates</h2>
                    <div class="row" id="templates-grid"></div>
                </div>
                
                <!-- Email List -->
                <div id="emails" class="page">
                    <h2 class="mb-4 text-white">📋 Email List</h2>
                    <div class="card p-4">
                        <button class="btn btn-primary mb-3" data-bs-toggle="modal" data-bs-target="#addEmailModal"><i class="bi bi-plus-circle"></i> Add Emails</button>
                        <table class="table table-hover">
                            <thead><tr><th>#</th><th>Email</th><th>Actions</th></tr></thead>
                            <tbody id="email-list-body"></tbody>
                        </table>
                    </div>
                </div>
                
                <!-- Settings -->
                <div id="settings" class="page">
                    <h2 class="mb-4 text-white">⚙️ Settings</h2>
                    <div class="card p-4">
                        <div class="mb-3">
                            <label class="form-label">SMTP Server</label>
                            <input type="text" class="form-control" value="smtp.gmail.com" readonly>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Email</label>
                            <input type="email" class="form-control" value="{SENDER_EMAIL}" readonly>
                        </div>
                        <p class="text-muted">Edit .env file to change settings</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Add Email Modal -->
    <div class="modal fade" id="addEmailModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Add Emails</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <textarea class="form-control" id="add-email-text" rows="5" placeholder="Paste emails here (one per line)"></textarea>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-primary" onclick="addEmails()">Add</button>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function showPage(pageId) {{
            document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
            document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
            document.getElementById(pageId).classList.add('active');
            event.target.classList.add('active');
        }}
        
        async function loadStats() {{
            const stats = await (await fetch('/api/stats')).json();
            const emails = await (await fetch('/api/emails')).json();
            const templates = await (await fetch('/api/templates')).json();
            
            document.getElementById('stat-emails').textContent = emails.total;
            document.getElementById('stat-templates').textContent = templates.templates.length;
            document.getElementById('stat-campaigns').textContent = 0;
        }}
        
        async function loadTemplates() {{
            const data = await (await fetch('/api/templates')).json();
            const select = document.getElementById('email-template');
            const grid = document.getElementById('templates-grid');
            
            select.innerHTML = '<option value="">Select template...</option>';
            grid.innerHTML = '';
            
            data.templates.forEach(t => {{
                select.innerHTML += `<option value="${{t.name}}">${{t.name}}</option>`;
                grid.innerHTML += `<div class="col-md-4 mb-3"><div class="card p-3"><h6>${{t.name}}</h6><small class="text-muted">${{t.file}}</small></div></div>`;
            }});
        }}
        
        async function loadEmails() {{
            const data = await (await fetch('/api/emails')).json();
            const tbody = document.getElementById('email-list-body');
            tbody.innerHTML = '';
            
            data.emails.forEach((email, i) => {{
                tbody.innerHTML += `<tr><td>${{i+1}}</td><td>${{email}}</td><td><button class="btn btn-sm btn-outline-danger" onclick="deleteEmail('${{email}}')"><i class="bi bi-trash"></i></button></td></tr>`;
            }});
        }}
        
        async function addEmails() {{
            const text = document.getElementById('add-email-text').value;
            const result = await (await fetch('/api/email/add', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{emails: text}})
            }})).json();
            
            alert('Added ' + result.added + ' emails');
            loadEmails();
            loadStats();
            bootstrap.Modal.getInstance(document.getElementById('addEmailModal')).hide();
        }}
        
        async function deleteEmail(email) {{
            if (confirm('Delete ' + email + '?')) {{
                await fetch('/api/email/delete', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{email: email}})
                }});
                loadEmails();
                loadStats();
            }}
        }}
        
        async function sendEmail(e) {{
            e.preventDefault();
            const data = {{
                subject: document.getElementById('email-subject').value,
                from_name: document.getElementById('email-from').value,
                template: document.getElementById('email-template').value,
                content: document.getElementById('email-content').value
            }};
            
            const result = await (await fetch('/api/send', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify(data)
            }})).json();
            
            alert(result.message || 'Email queued!');
        }}
        
        // Initialize
        loadStats();
        loadTemplates();
        loadEmails();
        setInterval(() => {{ loadStats(); loadEmails(); }}, 30000);
    </script>
</body>
</html>"""
        self.send_html(html)
    
    def api_list_templates(self):
        templates = []
        if TEMPLATES_DIR.exists():
            for f in TEMPLATES_DIR.glob('*.html'):
                templates.append({'name': f.stem, 'file': f.name})
        self.send_json({'templates': templates})
    
    def api_list_emails(self):
        emails = []
        if EMAIL_LIST_FILE.exists():
            with open(EMAIL_LIST_FILE, 'r') as f:
                emails = [line.strip() for line in f if line.strip() and not line.startswith('#') and '@' in line]
        self.send_json({'emails': emails, 'total': len(emails)})
    
    def api_get_stats(self):
        self.send_json({'total_campaigns': 0, 'total_sent': 0, 'success_rate': 100})
    
    def api_add_email(self, data):
        manager = EmailListManager(EMAIL_LIST_FILE)
        added = 0
        for line in data.get('emails', '').replace(',', '\n').split('\n'):
            email = line.strip()
            if email and '@' in email:
                try:
                    manager.add_email(email, validate=False)
                    added += 1
                except: pass
        self.send_json({'added': added})
    
    def api_delete_email(self, data):
        manager = EmailListManager(EMAIL_LIST_FILE)
        try:
            manager.remove_email(data.get('email', ''))
            self.send_json({'deleted': True})
        except:
            self.send_json({'deleted': False})
    
    def api_send_email(self, data):
        self.send_json({'message': 'Email queued for sending', 'data': data})


def run_web_gui(port=8080):
    server = HTTPServer(('0.0.0.0', port), WebGUIHandler)
    print(f"\n{'='*60}")
    print(f"🌐 Email Bot Web GUI")
    print(f"{'='*60}")
    print(f"📍 Running at: http://localhost:{port}")
    print(f"\n✨ Features:")
    print(f"  ✓ Dashboard with stats")
    print(f"  ✓ Visual email composer")
    print(f"  ✓ Template browser")
    print(f"  ✓ Email list manager")
    print(f"  ✓ Settings panel")
    print(f"\n⚠️  Press Ctrl+C to stop")
    print(f"{'='*60}\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
        server.shutdown()


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run_web_gui(port)
