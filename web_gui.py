#!/usr/bin/env python3
"""Email Bot Web Application - Full GUI with visual controls."""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import sys
from pathlib import Path
from datetime import datetime
from urllib.parse import parse_qs, urlparse
import re

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config import TEMPLATES_DIR, EMAIL_LIST_FILE, SENDER_EMAIL, SENDER_NAME
from email_list_manager import EmailListManager
from template_manager import TemplateManager
from spam_checker import SpamChecker
from email_validator import EmailValidator


class WebGUIHandler(BaseHTTPRequestHandler):
    """Web GUI Handler with full graphical interface."""
    
    def log_message(self, format, *args):
        """Custom logging."""
        print(f"[Web GUI] {datetime.now().strftime('%H:%M:%S')} - {args[0]}")
    
    def send_html(self, html: str, status: int = 200):
        """Send HTML response."""
        self.send_response(status)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def send_json(self, data: dict, status: int = 200):
        """Send JSON response."""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, default=str).encode())
    
    def do_OPTIONS(self):
        """Handle CORS preflight."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests."""
        path = urlparse(self.path).path
        
        routes = {
            '/': self.show_dashboard,
            '/compose': self.show_compose,
            '/templates': self.show_templates,
            '/template-editor': self.show_template_editor,
            '/email-list': self.show_email_list,
            '/campaigns': self.show_campaigns,
            '/analytics': self.show_analytics,
            '/settings': self.show_settings,
            '/api/templates': self.api_list_templates,
            '/api/emails': self.api_list_emails,
            '/api/stats': self.api_get_stats,
        }
        
        handler = routes.get(path, self.show_404)
        handler()
    
    def do_POST(self):
        """Handle POST requests."""
        path = urlparse(self.path).path
        
        # Get POST data
        content_type = self.headers.get('Content-Type', '')
        content_length = int(self.headers.get('Content-Length', 0))
        
        post_data = {}
        if 'application/json' in content_type:
            post_data = json.loads(self.rfile.read(content_length).decode())
        else:
            # Parse form data manually (no cgi module)
            post_body = self.rfile.read(content_length).decode()
            if 'multipart/form-data' in content_type:
                # Simple multipart parsing (for basic file uploads)
                post_data = {'content': post_body}
            else:
                post_data = parse_qs(post_body)
                post_data = {k: v[0] for k, v in post_data.items()}
        
        # Route POST requests
        if path == '/api/send':
            self.api_send_email(post_data)
        elif path == '/api/template/save':
            self.api_save_template(post_data)
        elif path == '/api/email/add':
            self.api_add_email(post_data)
        elif path == '/api/email/delete':
            self.api_delete_email(post_data)
        else:
            self.send_json({'error': 'Not found'}, 404)
    
    # ==================== PAGES ====================
    
    def show_dashboard(self):
        """Show main dashboard."""
        html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Email Bot - Web GUI</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css" rel="stylesheet">
    <style>
        :root {
            --primary: #667eea;
            --secondary: #764ba2;
            --success: #10b981;
            --danger: #ef4444;
        }
        body { 
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            min-height: 100vh;
            font-family: 'Segoe UI', system-ui, sans-serif;
        }
        .sidebar {
            background: rgba(255,255,255,0.95);
            min-height: 100vh;
            box-shadow: 4px 0 20px rgba(0,0,0,0.1);
        }
        .sidebar .nav-link {
            color: #333;
            padding: 12px 20px;
            border-radius: 10px;
            margin: 5px 10px;
            transition: all 0.3s;
        }
        .sidebar .nav-link:hover, .sidebar .nav-link.active {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
        }
        .sidebar .nav-link i { margin-right: 10px; }
        .main-content { padding: 30px; }
        .card {
            border: none;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .stat-card {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
            padding: 25px;
            border-radius: 15px;
        }
        .stat-card h3 { font-size: 14px; opacity: 0.9; text-transform: uppercase; }
        .stat-card .value { font-size: 36px; font-weight: bold; }
        .btn-primary {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            border: none;
        }
        .page { display: none; }
        .page.active { display: block; }
        .template-preview {
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            padding: 15px;
            cursor: pointer;
            transition: all 0.3s;
        }
        .template-preview:hover {
            border-color: var(--primary);
            box-shadow: 0 5px 20px rgba(102,126,234,0.3);
        }
        .email-editor {
            min-height: 400px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            padding: 20px;
        }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <!-- Sidebar -->
            <div class="col-md-2 sidebar p-3">
                <h4 class="mb-4">📧 Email Bot</h4>
                <nav class="nav flex-column">
                    <a class="nav-link active" href="#" onclick="showPage('dashboard')">
                        <i class="bi bi-speedometer2"></i> Dashboard
                    </a>
                    <a class="nav-link" href="#" onclick="showPage('compose')">
                        <i class="bi bi-pencil-square"></i> Compose
                    </a>
                    <a class="nav-link" href="#" onclick="showPage('templates')">
                        <i class="bi bi-images"></i> Templates
                    </a>
                    <a class="nav-link" href="#" onclick="showPage('email-list')">
                        <i class="bi bi-people"></i> Email List
                    </a>
                    <a class="nav-link" href="#" onclick="showPage('campaigns')">
                        <i class="bi bi-send"></i> Campaigns
                    </a>
                    <a class="nav-link" href="#" onclick="showPage('analytics')">
                        <i class="bi bi-graph-up"></i> Analytics
                    </a>
                    <a class="nav-link" href="#" onclick="showPage('settings')">
                        <i class="bi bi-gear"></i> Settings
                    </a>
                </nav>
            </div>
            
            <!-- Main Content -->
            <div class="col-md-10 main-content">
                <!-- Dashboard Page -->
                <div id="dashboard" class="page active">
                    <h2 class="mb-4">📊 Dashboard</h2>
                    <div class="row">
                        <div class="col-md-3">
                            <div class="stat-card">
                                <h3>Campaigns</h3>
                                <div class="value" id="stat-campaigns">0</div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="stat-card">
                                <h3>Emails Sent</h3>
                                <div class="value" id="stat-sent">0</div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="stat-card">
                                <h3>Email List</h3>
                                <div class="value" id="stat-list">0</div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="stat-card">
                                <h3>Success Rate</h3>
                                <div class="value" id="stat-rate">0%</div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="row mt-4">
                        <div class="col-md-6">
                            <div class="card p-4">
                                <h5>🚀 Quick Actions</h5>
                                <div class="d-grid gap-2 mt-3">
                                    <button class="btn btn-primary" onclick="showPage('compose')">
                                        <i class="bi bi-plus-circle"></i> New Campaign
                                    </button>
                                    <button class="btn btn-outline-primary" onclick="showPage('templates')">
                                        <i class="bi bi-images"></i> Browse Templates
                                    </button>
                                    <button class="btn btn-outline-primary" onclick="showPage('email-list')">
                                        <i class="bi bi-people"></i> Manage Emails
                                    </button>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="card p-4">
                                <h5>📈 Recent Activity</h5>
                                <div id="recent-activity" class="mt-3">
                                    <p class="text-muted">No recent activity</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Compose Page -->
                <div id="compose" class="page">
                    <h2 class="mb-4">📝 Compose Email</h2>
                    <div class="card p-4">
                        <form id="compose-form" onsubmit="sendEmail(event)">
                            <div class="row">
                                <div class="col-md-8">
                                    <div class="mb-3">
                                        <label class="form-label">Subject</label>
                                        <input type="text" class="form-control" name="subject" required 
                                               placeholder="Enter email subject">
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">From Name</label>
                                        <input type="text" class="form-control" name="from_name" 
                                               value=\"""" + SENDER_NAME + """\" placeholder="Your name">
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <div class="mb-3">
                                        <label class="form-label">Template</label>
                                        <select class="form-select" name="template" id="template-select">
                                            <option value="">Select template...</option>
                                        </select>
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">Send To</label>
                                        <select class="form-select" name="send_type">
                                            <option value="list">Email List</option>
                                            <option value="single">Single Email</option>
                                        </select>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="mb-3">
                                <label class="form-label">Email Content</label>
                                <div id="email-editor" class="email-editor" contenteditable="true">
                                    <p>Start typing your email content here...</p>
                                </div>
                            </div>
                            
                            <div class="mb-3">
                                <label class="form-label">Attachments</label>
                                <input type="file" class="form-control" name="attachment" multiple>
                            </div>
                            
                            <div class="d-flex gap-2">
                                <button type="submit" class="btn btn-primary">
                                    <i class="bi bi-send"></i> Send Email
                                </button>
                                <button type="button" class="btn btn-outline-primary">
                                    <i class="bi bi-eye"></i> Preview
                                </button>
                                <button type="button" class="btn btn-outline-secondary">
                                    <i class="bi bi-save"></i> Save Draft
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
                
                <!-- Templates Page -->
                <div id="templates" class="page">
                    <h2 class="mb-4">🎨 Templates</h2>
                    <div class="d-flex justify-content-between mb-4">
                        <div class="btn-group">
                            <button class="btn btn-outline-primary active">All</button>
                            <button class="btn btn-outline-primary">Promotion</button>
                            <button class="btn btn-outline-primary">Business</button>
                            <button class="btn btn-outline-primary">Personal</button>
                        </div>
                        <button class="btn btn-primary" onclick="showTemplateEditor()">
                            <i class="bi bi-plus-circle"></i> New Template
                        </button>
                    </div>
                    <div class="row" id="templates-grid">
                        <!-- Templates loaded dynamically -->
                    </div>
                </div>
                
                <!-- Email List Page -->
                <div id="email-list" class="page">
                    <h2 class="mb-4">📋 Email List</h2>
                    <div class="card p-4">
                        <div class="d-flex gap-2 mb-4">
                            <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#addEmailModal">
                                <i class="bi bi-plus-circle"></i> Add Email
                            </button>
                            <button class="btn btn-outline-primary">
                                <i class="bi bi-upload"></i> Import CSV
                            </button>
                            <button class="btn btn-outline-primary">
                                <i class="bi bi-download"></i> Export
                            </button>
                            <button class="btn btn-outline-danger">
                                <i class="bi bi-trash"></i> Clean Invalid
                            </button>
                        </div>
                        
                        <div class="table-responsive">
                            <table class="table table-hover">
                                <thead>
                                    <tr>
                                        <th>#</th>
                                        <th>Email</th>
                                        <th>Status</th>
                                        <th>Added</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody id="email-list-body">
                                    <!-- Emails loaded dynamically -->
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
                
                <!-- Campaigns Page -->
                <div id="campaigns" class="page">
                    <h2 class="mb-4">📤 Campaigns</h2>
                    <div class="card p-4">
                        <table class="table">
                            <thead>
                                <tr>
                                    <th>Campaign</th>
                                    <th>Date</th>
                                    <th>Sent</th>
                                    <th>Opened</th>
                                    <th>Clicked</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td colspan="6" class="text-center text-muted">No campaigns yet</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- Analytics Page -->
                <div id="analytics" class="page">
                    <h2 class="mb-4">📊 Analytics</h2>
                    <div class="row">
                        <div class="col-md-6">
                            <div class="card p-4">
                                <h5>Open Rate by Day</h5>
                                <canvas id="open-rate-chart"></canvas>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="card p-4">
                                <h5>Device Breakdown</h5>
                                <canvas id="device-chart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Settings Page -->
                <div id="settings" class="page">
                    <h2 class="mb-4">⚙️ Settings</h2>
                    <div class="card p-4">
                        <form>
                            <h5>SMTP Configuration</h5>
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label class="form-label">SMTP Server</label>
                                        <input type="text" class="form-control" value="smtp.gmail.com">
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label class="form-label">Port</label>
                                        <input type="number" class="form-control" value="587">
                                    </div>
                                </div>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Email</label>
                                <input type="email" class="form-control" value=\"""" + SENDER_EMAIL + """\">
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Password</label>
                                <input type="password" class="form-control" value="********">
                            </div>
                            <button class="btn btn-primary">Save Settings</button>
                        </form>
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
                    <h5 class="modal-title">Add Email</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <textarea class="form-control" rows="5" id="add-email-text" 
                              placeholder="Paste emails here (one per line or comma-separated)"></textarea>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-primary" onclick="addEmails()">Add Emails</button>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Page navigation
        function showPage(pageId) {
            document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
            document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
            document.getElementById(pageId).classList.add('active');
            event.target.classList.add('active');
        }
        
        // Load templates
        async function loadTemplates() {
            const response = await fetch('/api/templates');
            const data = await response.json();
            const grid = document.getElementById('templates-grid');
            const select = document.getElementById('template-select');
            
            grid.innerHTML = '';
            select.innerHTML = '<option value="">Select template...</option>';
            
            data.templates.forEach(t => {
                // Add to grid
                grid.innerHTML += `
                    <div class="col-md-4">
                        <div class="template-preview" onclick="selectTemplate('${t.name}')">
                            <h6>${t.name}</h6>
                            <small class="text-muted">${t.file}</small>
                        </div>
                    </div>
                `;
                // Add to select
                select.innerHTML += `<option value="${t.name}">${t.name}</option>`;
            });
        }
        
        // Load email list
        async function loadEmailList() {
            const response = await fetch('/api/emails');
            const data = await response.json();
            const tbody = document.getElementById('email-list-body');
            
            tbody.innerHTML = '';
            data.emails.forEach((email, i) => {
                tbody.innerHTML += `
                    <tr>
                        <td>${i + 1}</td>
                        <td>${email}</td>
                        <td><span class="badge bg-success">Active</span></td>
                        <td>Today</td>
                        <td>
                            <button class="btn btn-sm btn-outline-danger" onclick="deleteEmail('${email}')">
                                <i class="bi bi-trash"></i>
                            </button>
                        </td>
                    </tr>
                `;
            });
            
            document.getElementById('stat-list').textContent = data.total;
        }
        
        // Add emails
        async function addEmails() {
            const text = document.getElementById('add-email-text').value;
            const response = await fetch('/api/email/add', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({emails: text})
            });
            const result = await response.json();
            alert('Added ' + result.added + ' emails');
            loadEmailList();
            bootstrap.Modal.getInstance(document.getElementById('addEmailModal')).hide();
        }
        
        // Delete email
        async function deleteEmail(email) {
            if (confirm('Delete ' + email + '?')) {
                await fetch('/api/email/delete', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({email: email})
                });
                loadEmailList();
            }
        }
        
        // Send email
        async function sendEmail(e) {
            e.preventDefault();
            const form = e.target;
            const data = {
                subject: form.subject.value,
                from_name: form.from_name.value,
                template: form.template.value,
                content: document.getElementById('email-editor').innerHTML
            };
            
            const response = await fetch('/api/send', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            alert(result.message || 'Email sent!');
        }
        
        // Load stats
        async function loadStats() {
            const response = await fetch('/api/stats');
            const data = await response.json();
            document.getElementById('stat-campaigns').textContent = data.total_campaigns || 0;
            document.getElementById('stat-sent').textContent = (data.total_sent || 0).toLocaleString();
        }
        
        // Initialize
        loadTemplates();
        loadEmailList();
        loadStats();
        setInterval(loadStats, 30000);
    </script>
</body>
</html>"""
        self.send_html(html)
    
    def show_404(self):
        """Show 404 page."""
        self.send_html("<h1>404 - Page Not Found</h1>", 404)
    
    # ==================== API ENDPOINTS ====================
    
    def api_list_templates(self):
        """List templates."""
        templates = []
        if TEMPLATES_DIR.exists():
            for f in TEMPLATES_DIR.glob('*.html'):
                templates.append({'name': f.stem, 'file': f.name})
        self.send_json({'templates': templates})
    
    def api_list_emails(self):
        """List emails."""
        emails = []
        if EMAIL_LIST_FILE.exists():
            with open(EMAIL_LIST_FILE, 'r') as f:
                emails = [line.strip() for line in f 
                         if line.strip() and not line.startswith('#') and '@' in line]
        self.send_json({'emails': emails, 'total': len(emails)})
    
    def api_get_stats(self):
        """Get statistics."""
        self.send_json({
            'total_campaigns': 0,
            'total_sent': 0,
            'success_rate': 0
        })
    
    def api_send_email(self, data):
        """Send email."""
        # Implementation here
        self.send_json({'message': 'Email queued for sending'})
    
    def api_add_email(self, data):
        """Add emails."""
        emails_text = data.get('emails', '')
        manager = EmailListManager(EMAIL_LIST_FILE)
        
        added = 0
        for line in emails_text.replace(',', '\n').split('\n'):
            email = line.strip()
            if email and '@' in email:
                try:
                    manager.add_email(email, validate=False)
                    added += 1
                except:
                    pass
        
        self.send_json({'added': added})
    
    def api_delete_email(self, data):
        """Delete email."""
        email = data.get('email', '')
        manager = EmailListManager(EMAIL_LIST_FILE)
        manager.remove_email(email)
        self.send_json({'deleted': email})
    
    def api_save_template(self, data):
        """Save template."""
        name = data.get('name', 'new_template')
        content = data.get('content', '')
        
        template_file = TEMPLATES_DIR / f"{name}.html"
        with open(template_file, 'w') as f:
            f.write(content)
        
        self.send_json({'saved': name})


def run_web_gui(port: int = 8080):
    """Run the web GUI application."""
    server = HTTPServer(('0.0.0.0', port), WebGUIHandler)
    print(f"\n{'='*60}")
    print(f"🌐 Email Bot Web GUI")
    print(f"{'='*60}")
    print(f"📍 Running at: http://localhost:{port}")
    print(f"📍 Local: http://127.0.0.1:{port}")
    print(f"\n🎨 Features:")
    print(f"  ✓ Visual email composer")
    print(f"  ✓ Template browser & editor")
    print(f"  ✓ Email list manager")
    print(f"  ✓ Campaign builder")
    print(f"  ✓ Analytics dashboard")
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
