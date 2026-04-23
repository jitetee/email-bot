"""Enhanced HTML for Email Bot Web Application v5.0 - Advanced Features"""

def get_complete_html():
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="theme-color" content="#667eea">
    <title>Email Bot v5.0 - Enhanced Edition</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        :root { --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%); --sidebar-width: 280px; }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; background: #f5f7fa; overflow-x: hidden; }
        .mobile-nav-toggle { display: none; position: fixed; top: 15px; left: 15px; z-index: 1000; background: var(--primary-gradient); border: none; color: white; padding: 10px 15px; border-radius: 10px; cursor: pointer; }
        .sidebar { position: fixed; left: 0; top: 0; bottom: 0; width: var(--sidebar-width); background: white; box-shadow: 4px 0 20px rgba(0,0,0,0.08); z-index: 999; overflow-y: auto; transition: transform 0.3s ease; }
        .sidebar.show { transform: translateX(0); }
        .sidebar-brand { padding: 25px 20px; background: var(--primary-gradient); color: white; }
        .sidebar-brand h4 { margin: 0; font-weight: 700; }
        .menu-category { padding: 10px 20px 5px; color: #888; font-size: 11px; font-weight: 600; text-transform: uppercase; }
        .menu-item { display: flex; align-items: center; padding: 12px 20px; color: #333; cursor: pointer; border: none; background: none; width: 100%; text-align: left; }
        .menu-item:hover { background: #f8f9fa; }
        .menu-item.active { background: var(--primary-gradient); color: white; }
        .menu-item i { margin-right: 12px; font-size: 18px; width: 24px; }
        .submenu { background: #f8f9fa; padding: 10px 0; display: none; }
        .submenu.show { display: block; }
        .submenu-item { padding: 8px 20px 8px 56px; color: #555; display: block; cursor: pointer; }
        .submenu-item:hover { color: #667eea; background: #e9ecef; }
        .main-content { margin-left: var(--sidebar-width); min-height: 100vh; }
        .header { background: white; height: 60px; display: flex; align-items: center; justify-content: space-between; padding: 0 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); position: sticky; top: 0; z-index: 100; }
        .btn-custom { background: var(--primary-gradient); color: white; border: none; padding: 8px 20px; border-radius: 8px; font-weight: 600; }
        .content-area { padding: 30px; }
        .page { display: none; }
        .page.active { display: block; }
        .card { border: none; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.08); margin-bottom: 20px; }
        .card-header { background: white; border: none; padding: 20px; font-weight: 600; border-bottom: 1px solid #e9ecef; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .stat-card { background: var(--primary-gradient); color: white; padding: 25px; border-radius: 15px; }
        .stat-card h3 { font-size: 14px; opacity: 0.9; margin-bottom: 10px; }
        .stat-card .value { font-size: 36px; font-weight: bold; }
        .form-control, .form-select { border-radius: 10px; border: 2px solid #e9ecef; padding: 12px 15px; }
        .form-control:focus { border-color: #667eea; }
        .form-label { font-weight: 600; color: #333; margin-bottom: 8px; }
        .code-editor { font-family: 'Courier New', monospace; background: #1e1e1e; color: #d4d4d4; border-radius: 10px; padding: 15px; min-height: 400px; width: 100%; border: none; resize: vertical; }
        .toast-container { position: fixed; top: 20px; right: 20px; z-index: 1050; }
        .spinner-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: none; align-items: center; justify-content: center; z-index: 2000; }
        .spinner-overlay.show { display: flex; }
        .image-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 15px; }
        .image-card { border: 2px solid #e9ecef; border-radius: 10px; overflow: hidden; cursor: pointer; transition: all 0.2s; }
        .image-card:hover { border-color: #667eea; transform: translateY(-3px); }
        .image-card img { width: 100%; height: 120px; object-fit: cover; }
        .image-card .card-body { padding: 10px; }
        .template-preview { background: white; border-radius: 10px; padding: 20px; min-height: 500px; border: 2px solid #e9ecef; }
        .nav-tabs { border: none; margin-bottom: 20px; background: white; border-radius: 10px; padding: 10px; }
        .nav-tabs .nav-link { border: none; color: #555; padding: 10px 20px; border-radius: 8px; }
        .nav-tabs .nav-link.active { background: var(--primary-gradient); color: white; }
        .color-picker { width: 60px; height: 40px; border: none; border-radius: 8px; cursor: pointer; }
        .toolbar { background: #f8f9fa; padding: 15px; border-radius: 10px; margin-bottom: 15px; }
        .toolbar button { margin-right: 5px; margin-bottom: 5px; }
        @media (max-width: 992px) {
            .sidebar { transform: translateX(-100%); }
            .sidebar.show { transform: translateX(0); }
            .main-content { margin-left: 0; }
            .mobile-nav-toggle { display: block; }
            .header { padding: 0 20px 0 60px; }
        }
    </style>
</head>
<body>
    <button class="mobile-nav-toggle" onclick="toggleSidebar()"><i class="bi bi-list"></i></button>

    <div class="sidebar" id="sidebar">
        <div class="sidebar-brand">
            <h4>📧 Email Bot v5.0</h4>
            <p>Enhanced Edition</p>
        </div>
        <div class="menu-category">Main</div>
        <a class="menu-item active" onclick="showPage('dashboard')"><i class="bi bi-speedometer2"></i> Dashboard</a>
        
        <div class="menu-category">Email</div>
        <a class="menu-item" onclick="toggleSubmenu('email-submenu')"><i class="bi bi-send"></i> Send Emails <i class="bi bi-chevron-down ms-auto"></i></a>
        <div class="submenu" id="email-submenu">
            <button class="submenu-item" onclick="showPage('send-single')">Single Email</button>
            <button class="submenu-item" onclick="showPage('send-multiple')">Multiple Emails</button>
            <button class="submenu-item" onclick="showPage('send-bulk')">Bulk Campaign</button>
            <button class="submenu-item" onclick="showPage('send-schedule')">Schedule</button>
        </div>

        <a class="menu-item" onclick="toggleSubmenu('template-submenu')"><i class="bi bi-images"></i> Templates <i class="bi bi-chevron-down ms-auto"></i></a>
        <div class="submenu" id="template-submenu">
            <button class="submenu-item" onclick="showPage('templates-browse')">Browse</button>
            <button class="submenu-item" onclick="showPage('templates-editor')">Advanced Editor</button>
            <button class="submenu-item" onclick="showPage('templates-create')">Create New</button>
            <button class="submenu-item" onclick="showPage('templates-import')">Import HTML</button>
            <button class="submenu-item" onclick="showPage('templates-customize')">Customize</button>
        </div>

        <a class="menu-item" onclick="toggleSubmenu('media-submenu')"><i class="bi bi-collection"></i> Media <i class="bi bi-chevron-down ms-auto"></i></a>
        <div class="submenu" id="media-submenu">
            <button class="submenu-item" onclick="showPage('images-manager')">Image Manager</button>
            <button class="submenu-item" onclick="showPage('links-manager')">Link Tracker</button>
        </div>

        <a class="menu-item" onclick="toggleSubmenu('list-submenu')"><i class="bi bi-people"></i> Email List <i class="bi bi-chevron-down ms-auto"></i></a>
        <div class="submenu" id="list-submenu">
            <button class="submenu-item" onclick="showPage('list-view')">View All</button>
            <button class="submenu-item" onclick="showPage('list-add')">Add Emails</button>
            <button class="submenu-item" onclick="showPage('list-clean')">Clean & Dedup</button>
        </div>

        <div class="menu-category">Analytics</div>
        <a class="menu-item" onclick="showPage('analytics')"><i class="bi bi-graph-up"></i> Statistics</a>
        <a class="menu-item" onclick="showPage('campaigns')"><i class="bi bi-journal-text"></i> Campaigns</a>
        <a class="menu-item" onclick="showPage('bounces')"><i class="bi bi-exclamation-triangle"></i> Bounces</a>

        <div class="menu-category">Management</div>
        <a class="menu-item" onclick="showPage('smtp-accounts')"><i class="bi bi-hdd-network"></i> SMTP Accounts</a>
        <a class="menu-item" onclick="showPage('warmup')"><i class="bi bi-thermometer-half"></i> Warm-up</a>

        <div class="menu-category">Compliance</div>
        <a class="menu-item" onclick="showPage('domain-check')"><i class="bi bi-shield-check"></i> Domain Auth</a>
        <a class="menu-item" onclick="showPage('spam-check')"><i class="bi bi-exclamation-octagon"></i> Spam Check</a>
        <a class="menu-item" onclick="showPage('optin')"><i class="bi bi-person-check"></i> Double Opt-In</a>

        <div class="menu-category">Tools</div>
        <a class="menu-item" onclick="showPage('signatures')"><i class="bi bi-signature"></i> Signatures</a>
        <a class="menu-item" onclick="showPage('error-logs')"><i class="bi bi-bug"></i> Error Logs</a>
        <a class="menu-item" onclick="showPage('settings')"><i class="bi bi-gear"></i> Settings</a>
    </div>

    <div class="main-content">
        <div class="header">
            <div class="header-title"><h2 id="page-title">Dashboard</h2></div>
            <div class="header-actions">
                <button class="btn btn-custom" onclick="showPage('templates-editor')"><i class="bi bi-pencil-square"></i> New Template</button>
            </div>
        </div>

        <div class="content-area">
            <!-- DASHBOARD -->
            <div id="dashboard" class="page active">
                <div class="stats-grid">
                    <div class="stat-card"><h3><i class="bi bi-send"></i> Campaigns</h3><div class="value" id="stat-campaigns">0</div></div>
                    <div class="stat-card"><h3><i class="bi bi-envelope"></i> Emails Sent</h3><div class="value" id="stat-sent">0</div></div>
                    <div class="stat-card"><h3><i class="bi bi-people"></i> Email List</h3><div class="value" id="stat-emails">0</div></div>
                    <div class="stat-card"><h3><i class="bi bi-images"></i> Templates</h3><div class="value" id="stat-templates">0</div></div>
                </div>
                
                <!-- Charts Row -->
                <div class="row mb-4">
                    <div class="col-md-8">
                        <div class="card">
                            <div class="card-header"><i class="bi bi-graph-up"></i> Campaign Performance</div>
                            <div class="card-body">
                                <canvas id="campaign-chart" height="80"></canvas>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card">
                            <div class="card-header"><i class="bi bi-pie-chart"></i> Email Statistics</div>
                            <div class="card-body">
                                <canvas id="stats-pie-chart" height="200"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="row">
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header"><i class="bi bi-lightning"></i> Quick Actions</div>
                            <div class="card-body">
                                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px;">
                                    <button class="btn btn-custom" onclick="showPage('send-single')"><i class="bi bi-send"></i> Send Email</button>
                                    <button class="btn btn-custom" onclick="showPage('templates-editor')"><i class="bi bi-pencil-square"></i> Editor</button>
                                    <button class="btn btn-custom" onclick="showPage('images-manager')"><i class="bi bi-image"></i> Images</button>
                                    <button class="btn btn-custom" onclick="showPage('analytics')"><i class="bi bi-graph-up"></i> Analytics</button>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header"><i class="bi bi-table"></i> Recent Campaigns Table</div>
                            <div class="card-body">
                                <div style="max-height: 250px; overflow-y: auto;">
                                    <table class="table table-sm table-striped">
                                        <thead><tr><th>Campaign</th><th>Sent</th><th>Rate</th></tr></thead>
                                        <tbody id="recent-campaigns-body"></tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- SEND SINGLE EMAIL -->
            <div id="send-single" class="page">
                <div class="card">
                    <div class="card-header"><i class="bi bi-send"></i> Send Single Email</div>
                    <div class="card-body">
                        <form onsubmit="sendSingleEmail(event)">
                            <div class="alert alert-info mb-3">
                                <i class="bi bi-info-circle"></i> SMTP credentials are required to send emails. Leave blank to use server defaults.
                            </div>
                            <div class="row">
                                <div class="col-md-6 mb-3"><label class="form-label">Recipient Email</label><input type="email" class="form-control" id="single-to" required></div>
                                <div class="col-md-6 mb-3"><label class="form-label">From Name</label><input type="text" class="form-control" id="single-from" value="Your Company"></div>
                            </div>
                            <div class="row">
                                <div class="col-md-6 mb-3"><label class="form-label">Sender Email (SMTP)</label><input type="email" class="form-control" id="single-sender-email" placeholder="your@gmail.com"></div>
                                <div class="col-md-6 mb-3"><label class="form-label">App Password</label><input type="password" class="form-control" id="single-sender-password" placeholder="App password"></div>
                            </div>
                            <div class="mb-3"><label class="form-label">Subject</label><input type="text" class="form-control" id="single-subject" required></div>
                            <div class="mb-3"><label class="form-label">Template</label><select class="form-select" id="single-template" onchange="loadTemplateContent()"></select></div>
                            <div class="mb-3"><label class="form-label">Content</label><textarea class="form-control" id="single-content" rows="8"></textarea></div>
                            <div class="mb-3">
                                <label class="form-label">Tracking Options</label>
                                <div>
                                    <input type="checkbox" id="track-opens" checked> <label for="track-opens">Track Opens</label>
                                    <input type="checkbox" id="track-clicks" checked> <label for="track-clicks">Track Clicks</label>
                                </div>
                            </div>
                            <button type="submit" class="btn btn-custom"><i class="bi bi-send"></i> Send Email</button>
                        </form>
                    </div>
                </div>
            </div>

            <!-- SEND MULTIPLE -->
            <div id="send-multiple" class="page">
                <div class="card">
                    <div class="card-header"><i class="bi bi-send"></i> Send to Multiple Recipients</div>
                    <div class="card-body">
                        <form onsubmit="sendMultipleEmails(event)">
                            <div class="mb-3"><label class="form-label">Recipients (one per line)</label><textarea class="form-control" id="multiple-recipients" rows="5" placeholder="user1@example.com&#10;user2@example.com"></textarea></div>
                            <div class="mb-3"><label class="form-label">Subject</label><input type="text" class="form-control" id="multiple-subject" required></div>
                            <div class="mb-3"><label class="form-label">Template</label><select class="form-select" id="multiple-template"></select></div>
                            <button type="submit" class="btn btn-custom"><i class="bi bi-send"></i> Send to All</button>
                        </form>
                    </div>
                </div>
            </div>

            <!-- SEND BULK -->
            <div id="send-bulk" class="page">
                <div class="card">
                    <div class="card-header"><i class="bi bi-send-fill"></i> Send Bulk Campaign</div>
                    <div class="card-body">
                        <form onsubmit="sendBulkEmail(event)">
                            <div class="row">
                                <div class="col-md-6 mb-3"><label class="form-label">Template</label><select class="form-select" id="bulk-template"></select></div>
                                <div class="col-md-6 mb-3"><label class="form-label">Subject</label><input type="text" class="form-control" id="bulk-subject" required></div>
                            </div>
                            <div class="row">
                                <div class="col-md-4 mb-3"><label class="form-label">Batch Size</label><input type="number" class="form-control" id="bulk-batch" value="25"></div>
                                <div class="col-md-4 mb-3"><label class="form-label">Delay Min (s)</label><input type="number" class="form-control" id="bulk-delay-min" value="1"></div>
                                <div class="col-md-4 mb-3"><label class="form-label">Delay Max (s)</label><input type="number" class="form-control" id="bulk-delay-max" value="3"></div>
                            </div>
                            <button type="submit" class="btn btn-custom"><i class="bi bi-rocket-takeoff"></i> Start Campaign</button>
                        </form>
                    </div>
                </div>
            </div>

            <!-- SCHEDULE -->
            <div id="send-schedule" class="page">
                <div class="card">
                    <div class="card-header"><i class="bi bi-calendar-event"></i> Schedule Campaign</div>
                    <div class="card-body">
                        <form onsubmit="scheduleCampaign(event)">
                            <div class="mb-3"><label class="form-label">Campaign Name</label><input type="text" class="form-control" id="schedule-name" required></div>
                            <div class="row">
                                <div class="col-md-6 mb-3"><label class="form-label">Template</label><select class="form-select" id="schedule-template"></select></div>
                                <div class="col-md-6 mb-3"><label class="form-label">Subject</label><input type="text" class="form-control" id="schedule-subject" required></div>
                            </div>
                            <div class="mb-3"><label class="form-label">Scheduled Date & Time</label><input type="datetime-local" class="form-control" id="schedule-datetime" required></div>
                            <div class="mb-3"><label class="form-label">Sender Email</label><input type="email" class="form-control" id="schedule-sender" required></div>
                            <button type="submit" class="btn btn-custom"><i class="bi bi-calendar-check"></i> Schedule</button>
                        </form>
                    </div>
                </div>
            </div>

            <!-- TEMPLATES BROWSE -->
            <div id="templates-browse" class="page">
                <div class="card">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <span><i class="bi bi-images"></i> Browse Templates</span>
                        <button class="btn btn-sm btn-custom" onclick="showPage('templates-create')"><i class="bi bi-plus-circle"></i> New</button>
                    </div>
                    <div class="card-body">
                        <div class="row" id="templates-grid"></div>
                    </div>
                </div>
            </div>

            <!-- ADVANCED TEMPLATE EDITOR -->
            <div id="templates-editor" class="page">
                <div class="card">
                    <div class="card-header"><i class="bi bi-pencil-square"></i> Advanced Template Editor</div>
                    <div class="card-body">
                        <ul class="nav nav-tabs">
                            <li class="nav-item"><a class="nav-link active" data-bs-toggle="tab" href="#editor-code">Code Editor</a></li>
                            <li class="nav-item"><a class="nav-link" data-bs-toggle="tab" href="#editor-preview">Live Preview</a></li>
                            <li class="nav-item"><a class="nav-link" data-bs-toggle="tab" href="#editor-images">Images</a></li>
                            <li class="nav-item"><a class="nav-link" data-bs-toggle="tab" href="#editor-links">Links</a></li>
                        </ul>
                        <div class="tab-content">
                            <div class="tab-pane fade show active" id="editor-code">
                                <div class="toolbar">
                                    <button class="btn btn-sm btn-outline-primary" onclick="insertTag('h1')"><i class="bi bi-type-h1"></i> H1</button>
                                    <button class="btn btn-sm btn-outline-primary" onclick="insertTag('h2')"><i class="bi bi-type-h2"></i> H2</button>
                                    <button class="btn btn-sm btn-outline-primary" onclick="insertTag('p')"><i class="bi bi-paragraph"></i> Paragraph</button>
                                    <button class="btn btn-sm btn-outline-primary" onclick="insertTag('a')"><i class="bi bi-link-45deg"></i> Link</button>
                                    <button class="btn btn-sm btn-outline-primary" onclick="insertTag('img')"><i class="bi bi-image"></i> Image</button>
                                    <button class="btn btn-sm btn-outline-primary" onclick="insertTag('button')"><i class="bi bi-square"></i> Button</button>
                                    <button class="btn btn-sm btn-outline-success" onclick="insertVariable()"><i class="bi bi-braces"></i> Insert Variable</button>
                                    <button class="btn btn-sm btn-outline-danger" onclick="formatHTML()"><i class="bi bi-magic"></i> Format HTML</button>
                                </div>
                                <textarea class="code-editor" id="template-editor-html" rows="25" placeholder="Paste or write your HTML here..."></textarea>
                                <div class="mt-3">
                                    <button class="btn btn-custom" onclick="saveTemplate()"><i class="bi bi-save"></i> Save Template</button>
                                    <button class="btn btn-outline-primary" onclick="updatePreview()"><i class="bi bi-eye"></i> Update Preview</button>
                                </div>
                            </div>
                            <div class="tab-pane fade" id="editor-preview">
                                <div id="template-live-preview" class="template-preview"></div>
                            </div>
                            <div class="tab-pane fade" id="editor-images">
                                <div id="images-container" class="image-grid"></div>
                                <p class="text-muted mt-3"><small>Click an image to insert its URL into the editor</small></p>
                            </div>
                            <div class="tab-pane fade" id="editor-links">
                                <div id="links-container"></div>
                                <p class="text-muted mt-3"><small>Click a link to insert its URL into the editor</small></p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- CREATE TEMPLATE -->
            <div id="templates-create" class="page">
                <div class="card">
                    <div class="card-header"><i class="bi bi-plus-circle"></i> Create New Template</div>
                    <div class="card-body">
                        <form onsubmit="createTemplate(event)">
                            <div class="row">
                                <div class="col-md-6 mb-3"><label class="form-label">Template Name</label><input type="text" class="form-control" id="template-name" required></div>
                                <div class="col-md-6 mb-3"><label class="form-label">Subject</label><input type="text" class="form-control" id="template-subject"></div>
                            </div>
                            <div class="mb-3"><label class="form-label">HTML Content</label><textarea class="code-editor" id="template-html" rows="20" placeholder="<!DOCTYPE html>..."></textarea></div>
                            <button type="submit" class="btn btn-custom"><i class="bi bi-save"></i> Save Template</button>
                        </form>
                    </div>
                </div>
            </div>

            <!-- IMPORT HTML -->
            <div id="templates-import" class="page">
                <div class="card">
                    <div class="card-header"><i class="bi bi-clipboard-data"></i> Import HTML Template</div>
                    <div class="card-body">
                        <form onsubmit="importTemplate(event)">
                            <div class="mb-3"><label class="form-label">Template Name</label><input type="text" class="form-control" id="import-name" required></div>
                            <div class="mb-3"><label class="form-label">Subject</label><input type="text" class="form-control" id="import-subject"></div>
                            <div class="mb-3"><label class="form-label">Paste HTML Code</label><textarea class="code-editor" id="import-html" rows="20" placeholder="Paste your HTML code here..."></textarea></div>
                            <button type="submit" class="btn btn-custom"><i class="bi bi-download"></i> Import Template</button>
                        </form>
                    </div>
                </div>
            </div>

            <!-- CUSTOMIZE TEMPLATE -->
            <div id="templates-customize" class="page">
                <div class="card">
                    <div class="card-header"><i class="bi bi-palette"></i> Customize Template</div>
                    <div class="card-body">
                        <div class="mb-3"><label class="form-label">Select Template</label><select class="form-select" id="customize-template-select"></select></div>
                        <div class="row">
                            <div class="col-md-6">
                                <h5>Colors</h5>
                                <div class="mb-2"><label>Primary Color</label><input type="color" class="color-picker" id="customize-primary" value="#667eea"></div>
                                <div class="mb-2"><label>Secondary Color</label><input type="color" class="color-picker" id="customize-secondary" value="#764ba2"></div>
                            </div>
                            <div class="col-md-6">
                                <h5>Content Placeholders</h5>
                                <div class="mb-2"><input type="text" class="form-control" placeholder="Company Name" id="customize-company"></div>
                                <div class="mb-2"><input type="text" class="form-control" placeholder="Unsubscribe URL" id="customize-unsubscribe"></div>
                            </div>
                        </div>
                        <button class="btn btn-custom mt-3" onclick="customizeTemplate()"><i class="bi bi-magic"></i> Apply Customizations</button>
                        <div id="customize-result" class="mt-3"></div>
                    </div>
                </div>
            </div>

            <!-- IMAGE MANAGER -->
            <div id="images-manager" class="page">
                <div class="card">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <span><i class="bi bi-collection"></i> Image Manager</span>
                        <button class="btn btn-sm btn-custom" onclick="document.getElementById('image-upload').click()"><i class="bi bi-upload"></i> Upload Image</button>
                        <input type="file" id="image-upload" accept="image/*" style="display: none;" onchange="uploadImage()">
                    </div>
                    <div class="card-body">
                        <div id="images-grid" class="image-grid"></div>
                    </div>
                </div>
            </div>

            <!-- LINK TRACKER -->
            <div id="links-manager" class="page">
                <div class="card">
                    <div class="card-header"><i class="bi bi-link-45deg"></i> Link Tracker</div>
                    <div class="card-body">
                        <form onsubmit="addTrackedLink(event)" class="mb-4">
                            <div class="row">
                                <div class="col-md-4"><input type="text" class="form-control" id="link-name" placeholder="Link Name"></div>
                                <div class="col-md-6"><input type="url" class="form-control" id="link-url" placeholder="https://example.com" required></div>
                                <div class="col-md-2"><button type="submit" class="btn btn-custom w-100"><i class="bi bi-plus"></i> Add</button></div>
                            </div>
                        </form>
                        <div id="links-list"></div>
                    </div>
                </div>
            </div>

            <!-- EMAIL LIST -->
            <div id="list-view" class="page">
                <div class="card">
                    <div class="card-header"><i class="bi bi-people"></i> Email List</div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-hover">
                                <thead><tr><th>#</th><th>Email</th><th>Actions</th></tr></thead>
                                <tbody id="email-list-body"></tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>

            <!-- ADD EMAILS -->
            <div id="list-add" class="page">
                <div class="card">
                    <div class="card-header"><i class="bi bi-plus-circle"></i> Add Emails</div>
                    <div class="card-body">
                        <form onsubmit="addEmail(event)">
                            <div class="mb-3"><label class="form-label">Email Address</label><input type="email" class="form-control" id="add-email-single" required></div>
                            <button type="submit" class="btn btn-custom"><i class="bi bi-plus-circle"></i> Add Email</button>
                        </form>
                        <hr>
                        <form onsubmit="addMultipleEmails(event)">
                            <div class="mb-3"><label class="form-label">Multiple Emails (one per line)</label><textarea class="form-control" id="add-emails-multiple" rows="8"></textarea></div>
                            <button type="submit" class="btn btn-custom"><i class="bi bi-people-fill"></i> Add All</button>
                        </form>
                    </div>
                </div>
            </div>

            <!-- CLEAN EMAILS -->
            <div id="list-clean" class="page">
                <div class="card">
                    <div class="card-header"><i class="bi bi-trash"></i> Clean & Deduplicate</div>
                    <div class="card-body">
                        <button class="btn btn-custom me-2" onclick="cleanInvalidEmails()"><i class="bi bi-broom"></i> Clean Invalid</button>
                        <button class="btn btn-custom" onclick="dedupEmails()"><i class="bi bi-files"></i> Remove Duplicates</button>
                    </div>
                </div>
            </div>

            <!-- ANALYTICS -->
            <div id="analytics" class="page">
                <div class="card">
                    <div class="card-header"><i class="bi bi-graph-up"></i> Complete Analytics Dashboard</div>
                    <div class="card-body">
                        <!-- Summary Stats -->
                        <div class="stats-grid mb-4">
                            <div class="stat-card" style="background: linear-gradient(135deg, #667eea, #764ba2);"><h3>Campaigns</h3><div class="value" id="analytics-campaigns">0</div></div>
                            <div class="stat-card" style="background: linear-gradient(135deg, #f093fb, #f5576c);"><h3>Emails Sent</h3><div class="value" id="analytics-sent">0</div></div>
                            <div class="stat-card" style="background: linear-gradient(135deg, #4facfe, #00f2fe);"><h3>Success Rate</h3><div class="value" id="analytics-rate">100%</div></div>
                            <div class="stat-card" style="background: linear-gradient(135deg, #43e97b, #38f9d7);"><h3>Templates</h3><div class="value" id="analytics-templates">0</div></div>
                        </div>
                        
                        <!-- Charts Grid -->
                        <div class="row mb-4">
                            <div class="col-md-8">
                                <div class="card">
                                    <div class="card-header">Daily Email Activity</div>
                                    <div class="card-body">
                                        <canvas id="daily-activity-chart" height="100"></canvas>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="card">
                                    <div class="card-header">Bounce Analysis</div>
                                    <div class="card-body">
                                        <canvas id="bounce-chart" height="200"></canvas>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="row">
                            <div class="col-md-6">
                                <div class="card">
                                    <div class="card-header">Campaign Success Rates</div>
                                    <div class="card-body">
                                        <canvas id="success-rate-chart" height="150"></canvas>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="card">
                                    <div class="card-header">Resource Distribution</div>
                                    <div class="card-body">
                                        <canvas id="resource-chart" height="200"></canvas>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Detailed Data Table -->
                        <div class="card mt-4">
                            <div class="card-header d-flex justify-content-between align-items-center">
                                <span><i class="bi bi-table"></i> Campaign Details</span>
                                <button class="btn btn-sm btn-outline-primary" onclick="loadAnalytics()"><i class="bi bi-arrow-clockwise"></i> Refresh</button>
                            </div>
                            <div class="card-body">
                                <div style="max-height: 400px; overflow-y: auto;">
                                    <table class="table table-hover">
                                        <thead>
                                            <tr>
                                                <th>Campaign</th>
                                                <th>Date</th>
                                                <th>Sent</th>
                                                <th>Success Rate</th>
                                                <th>Bounces</th>
                                                <th>Status</th>
                                            </tr>
                                        </thead>
                                        <tbody id="campaigns-table-body"></tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- CAMPAIGNS -->
            <div id="campaigns" class="page">
                <div class="card">
                    <div class="card-header"><i class="bi bi-journal-text"></i> Campaign Logs</div>
                    <div class="card-body"><div id="campaign-logs"></div></div>
                </div>
            </div>

            <!-- BOUNCES -->
            <div id="bounces" class="page">
                <div class="card">
                    <div class="card-header"><i class="bi bi-exclamation-triangle"></i> Bounce Reports</div>
                    <div class="card-body"><div id="bounce-list"></div></div>
                </div>
            </div>

            <!-- SMTP ACCOUNTS -->
            <div id="smtp-accounts" class="page">
                <div class="card">
                    <div class="card-header"><i class="bi bi-hdd-network"></i> SMTP Accounts</div>
                    <div class="card-body"><div id="smtp-accounts-list"></div></div>
                </div>
            </div>

            <!-- WARMUP -->
            <div id="warmup" class="page">
                <div class="card">
                    <div class="card-header"><i class="bi bi-thermometer-half"></i> Warm-up Sessions</div>
                    <div class="card-body"><div id="warmup-list"></div></div>
                </div>
            </div>

            <!-- DOMAIN CHECK -->
            <div id="domain-check" class="page">
                <div class="card">
                    <div class="card-header"><i class="bi bi-shield-check"></i> Domain Authentication</div>
                    <div class="card-body">
                        <form onsubmit="checkDomain(event)">
                            <div class="row">
                                <div class="col-md-8"><input type="text" class="form-control" id="domain-name" placeholder="example.com" required></div>
                                <div class="col-md-4"><button type="submit" class="btn btn-custom w-100"><i class="bi bi-search"></i> Check</button></div>
                            </div>
                        </form>
                        <div id="domain-results" class="mt-3"></div>
                    </div>
                </div>
            </div>

            <!-- SPAM CHECK -->
            <div id="spam-check" class="page">
                <div class="card">
                    <div class="card-header"><i class="bi bi-exclamation-octagon"></i> Spam Score Check</div>
                    <div class="card-body">
                        <form onsubmit="checkSpam(event)">
                            <div class="mb-3"><input type="text" class="form-control" id="spam-subject" placeholder="Subject Line"></div>
                            <div class="mb-3"><textarea class="form-control" id="spam-content" rows="8" placeholder="Email content..."></textarea></div>
                            <button type="submit" class="btn btn-custom"><i class="bi bi-search"></i> Check Spam Score</button>
                        </form>
                        <div id="spam-results" class="mt-3"></div>
                    </div>
                </div>
            </div>

            <!-- OPTIN -->
            <div id="optin" class="page">
                <div class="card">
                    <div class="card-header"><i class="bi bi-person-check"></i> Double Opt-In</div>
                    <div class="card-body">
                        <form onsubmit="optinSubscribe(event)">
                            <div class="mb-3"><input type="email" class="form-control" id="optin-email" placeholder="Email address" required></div>
                            <button type="submit" class="btn btn-custom"><i class="bi bi-person-plus"></i> Subscribe</button>
                        </form>
                    </div>
                </div>
            </div>

            <!-- SIGNATURES -->
            <div id="signatures" class="page">
                <div class="card">
                    <div class="card-header"><i class="bi bi-signature"></i> Email Signature Creator</div>
                    <div class="card-body">
                        <form onsubmit="createSignature(event)">
                            <div class="row">
                                <div class="col-md-6 mb-3"><label class="form-label">Name</label><input type="text" class="form-control" id="sig-name" required></div>
                                <div class="col-md-6 mb-3"><label class="form-label">Title</label><input type="text" class="form-control" id="sig-title"></div>
                            </div>
                            <div class="mb-3"><label class="form-label">Company</label><input type="text" class="form-control" id="sig-company"></div>
                            <button type="submit" class="btn btn-custom"><i class="bi bi-magic"></i> Create Signature</button>
                        </form>
                        <div id="signature-result" class="mt-3"></div>
                    </div>
                </div>
            </div>

            <!-- ERROR LOGS -->
            <div id="error-logs" class="page">
                <div class="card">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <span><i class="bi bi-bug"></i> Error Logs</span>
                        <div>
                            <button class="btn btn-sm btn-outline-danger me-2" onclick="clearErrors()"><i class="bi bi-trash"></i> Clear Logs</button>
                            <button class="btn btn-sm btn-outline-primary" onclick="loadErrors()"><i class="bi bi-arrow-clockwise"></i> Refresh</button>
                        </div>
                    </div>
                    <div class="card-body">
                        <div class="alert alert-info" id="error-log-info">Loading error logs...</div>
                        <div id="error-log-container" style="max-height: 500px; overflow-y: auto; background: #1e1e1e; color: #d4d4d4; padding: 15px; border-radius: 10px; font-family: 'Courier New', monospace; font-size: 13px;">
                            <p class="text-muted">No errors logged yet</p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- SETTINGS -->
            <div id="settings" class="page">
                <div class="card">
                    <div class="card-header"><i class="bi bi-gear"></i> Settings</div>
                    <div class="card-body">
                        <form onsubmit="saveSettings(event)">
                            <div class="row">
                                <div class="col-md-6 mb-3"><label class="form-label">SMTP Server</label><input type="text" class="form-control" id="setting-smtp-server" value="smtp.gmail.com"></div>
                                <div class="col-md-6 mb-3"><label class="form-label">SMTP Port</label><input type="number" class="form-control" id="setting-smtp-port" value="587"></div>
                            </div>
                            <div class="row">
                                <div class="col-md-6 mb-3"><label class="form-label">Sender Email</label><input type="email" class="form-control" id="setting-sender-email"></div>
                                <div class="col-md-6 mb-3"><label class="form-label">Sender Name</label><input type="text" class="form-control" id="setting-sender-name" value="Your Company"></div>
                            </div>
                            <button type="submit" class="btn btn-custom"><i class="bi bi-save"></i> Save Settings</button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="toast-container" id="toast-container"></div>
    <div class="spinner-overlay" id="loading-overlay"><div class="spinner-border text-light" style="width: 3rem; height: 3rem;"></div></div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Navigation
        function showPage(pageId) {
            document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
            document.querySelectorAll('.menu-item').forEach(m => m.classList.remove('active'));
            document.getElementById(pageId).classList.add('active');
            const titles = {
                'dashboard': 'Dashboard', 'send-single': 'Send Single Email', 'send-multiple': 'Send Multiple Emails',
                'send-bulk': 'Send Bulk Campaign', 'send-schedule': 'Schedule Campaign',
                'templates-browse': 'Browse Templates', 'templates-editor': 'Advanced Template Editor',
                'templates-create': 'Create Template', 'templates-import': 'Import HTML', 'templates-customize': 'Customize Template',
                'images-manager': 'Image Manager', 'links-manager': 'Link Tracker',
                'list-view': 'Email List', 'list-add': 'Add Emails', 'list-clean': 'Clean & Dedup',
                'analytics': 'Statistics', 'campaigns': 'Campaign Logs', 'bounces': 'Bounce Reports',
                'smtp-accounts': 'SMTP Accounts', 'warmup': 'Warm-up Sessions',
                'domain-check': 'Domain Authentication', 'spam-check': 'Spam Check', 'optin': 'Double Opt-In',
                'signatures': 'Email Signatures', 'settings': 'Settings'
            };
            document.getElementById('page-title').textContent = titles[pageId] || 'Email Bot';
            if (window.innerWidth <= 992) document.getElementById('sidebar').classList.remove('show');
            loadPageData(pageId);
        }

        function toggleSubmenu(id) { document.getElementById(id).classList.toggle('show'); }
        function toggleSidebar() { document.getElementById('sidebar').classList.toggle('show'); }

        function showToast(msg, type = 'success') {
            const toast = document.createElement('div');
            toast.className = 'toast show align-items-center text-white bg-' + (type === 'success' ? 'success' : 'danger') + ' border-0';
            toast.innerHTML = '<div class="d-flex"><div class="toast-body">' + msg + '</div><button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button></div>';
            document.getElementById('toast-container').appendChild(toast);
            setTimeout(() => toast.remove(), 3000);
        }

        function showLoading() { document.getElementById('loading-overlay').classList.add('show'); }
        function hideLoading() { document.getElementById('loading-overlay').classList.remove('show'); }

        // Error Log Functions
        async function loadErrors() {
            try {
                const data = await (await fetch('/api/errors')).json();
                const container = document.getElementById('error-log-container');
                const info = document.getElementById('error-log-info');
                
                if (info) info.innerHTML = 'Log file: ' + (data.log_file || 'N/A') + ' | Total errors: ' + (data.total || 0);
                
                if (container) {
                    if (data.errors && data.errors.length > 0) {
                        container.innerHTML = '';
                        data.errors.forEach(err => {
                            const div = document.createElement('div');
                            div.style.marginBottom = '10px';
                            div.style.padding = '10px';
                            div.style.borderLeft = '3px solid #f5576c';
                            div.style.background = 'rgba(245, 87, 108, 0.1)';
                            div.textContent = err.trim();
                            container.appendChild(div);
                        });
                        container.scrollTop = container.scrollHeight;
                    } else {
                        container.innerHTML = '<p class="text-muted">No errors logged yet. Everything is running smoothly!</p>';
                    }
                }
            } catch (e) {
                console.error('Failed to load errors:', e);
                showToast('Failed to load errors', 'error');
            }
        }

        async function clearErrors() {
            if (!confirm('Clear all error logs?')) return;
            try {
                await (await fetch('/api/errors/clear', {method: 'POST'})).json();
                showToast('Error logs cleared!');
                loadErrors();
            } catch (e) {
                // Fallback: just reload
                loadErrors();
                showToast('Logs refreshed');
            }
        }

        // Data Loading
        function loadPageData(pageId) {
            if (['dashboard', 'analytics'].includes(pageId)) loadDashboard();
            if (['templates-browse', 'templates-editor', 'templates-create', 'templates-customize', 'send-single', 'send-multiple', 'send-bulk', 'send-schedule'].includes(pageId)) loadTemplates();
            if (pageId === 'list-view') loadEmails();
            if (pageId === 'templates-editor') { loadImages(); loadLinks(); }
            if (pageId === 'images-manager') loadImages();
            if (pageId === 'links-manager') loadLinks();
            if (pageId === 'error-logs') loadErrors();
            if (pageId === 'smtp-accounts') loadSMTPAccounts();
            if (pageId === 'warmup') loadWarmup();
            if (pageId === 'bounces') loadBounces();
            if (pageId === 'analytics') setTimeout(() => loadAnalytics(), 100);
        }

        async function loadDashboard() {
            try {
                const stats = await (await fetch('/api/stats')).json();
                document.getElementById('stat-campaigns').textContent = stats.total_campaigns || 0;
                document.getElementById('stat-sent').textContent = (stats.total_sent || 0).toLocaleString();
                document.getElementById('stat-emails').textContent = (stats.email_count || 0).toLocaleString();
                document.getElementById('stat-templates').textContent = (stats.template_count || 0).toLocaleString();
                if (document.getElementById('analytics-campaigns')) {
                    document.getElementById('analytics-campaigns').textContent = stats.total_campaigns || 0;
                    document.getElementById('analytics-sent').textContent = (stats.total_sent || 0).toLocaleString();
                    document.getElementById('analytics-rate').textContent = (stats.success_rate || 100) + '%';
                }
            } catch (e) { console.error(e); }
        }

        async function loadTemplates() {
            try {
                const data = await (await fetch('/api/templates')).json();
                const templates = data.templates || [];
                const selects = ['single-template', 'multiple-template', 'bulk-template', 'schedule-template', 'customize-template-select'];
                selects.forEach(id => {
                    const sel = document.getElementById(id);
                    if (sel) {
                        sel.innerHTML = '<option value="">Select template...</option>';
                        templates.forEach(t => { sel.innerHTML += '<option value="' + t.name + '">' + t.name + '</option>'; });
                    }
                });
                const grid = document.getElementById('templates-grid');
                if (grid) {
                    grid.innerHTML = '';
                    templates.forEach(t => {
                        grid.innerHTML += '<div class="col-md-4 mb-3"><div class="card"><div class="card-body"><h6>' + t.name + '</h6><small class="text-muted">' + (t.file || '') + '</small><div class="mt-2"><button class="btn btn-sm btn-outline-primary" onclick="editTemplate(\\'' + t.name + '\\')"><i class="bi bi-pencil"></i> Edit</button> <button class="btn btn-sm btn-outline-danger" onclick="deleteTemplate(\\'' + t.name + '\\')"><i class="bi bi-trash"></i></button></div></div></div></div>';
                    });
                }
            } catch (e) { console.error(e); }
        }

        async function loadEmails() {
            try {
                const data = await (await fetch('/api/emails')).json();
                const emails = data.emails || [];
                const tbody = document.getElementById('email-list-body');
                tbody.innerHTML = '';
                emails.forEach((email, i) => {
                    tbody.innerHTML += '<tr><td>' + (i + 1) + '</td><td>' + email + '</td><td><button class="btn btn-sm btn-outline-danger" onclick="deleteEmail(\\'' + email + '\\')"><i class="bi bi-trash"></i></button></td></tr>';
                });
            } catch (e) { console.error(e); }
        }

        async function loadImages() {
            try {
                const data = await (await fetch('/api/images')).json();
                const images = data.images || [];
                const grid = document.getElementById('images-grid');
                const editorGrid = document.getElementById('images-container');
                if (grid) {
                    grid.innerHTML = '';
                    images.forEach(img => {
                        grid.innerHTML += '<div class="image-card"><img src="' + img.url + '" alt="' + img.name + '"><div class="card-body"><small>' + img.name + '</small><br><button class="btn btn-sm btn-outline-primary mt-1" onclick="insertImage(\\'' + img.url + '\\')"><i class="bi bi-plus"></i> Insert</button></div></div>';
                    });
                }
                if (editorGrid) {
                    editorGrid.innerHTML = grid.innerHTML;
                }
            } catch (e) { console.error(e); }
        }

        async function loadLinks() {
            try {
                const data = await (await fetch('/api/links')).json();
                const links = data.links || [];
                const list = document.getElementById('links-list');
                const editorList = document.getElementById('links-container');
                if (list) {
                    list.innerHTML = '<table class="table"><thead><tr><th>Name</th><th>URL</th><th>Clicks</th><th>Actions</th></tr></thead><tbody>';
                    links.forEach(link => {
                        list.innerHTML += '<tr><td>' + link.name + '</td><td><a href="' + link.url + '" target="_blank">' + link.url + '</a></td><td>' + (link.clicks || 0) + '</td><td><button class="btn btn-sm btn-outline-primary" onclick="insertLink(\\'' + link.url + '\\')"><i class="bi bi-plus"></i></button></td></tr>';
                    });
                    list.innerHTML += '</tbody></table>';
                }
                if (editorList) {
                    editorList.innerHTML = list.innerHTML;
                }
            } catch (e) { console.error(e); }
        }

        async function loadSMTPAccounts() {
            try {
                const data = await (await fetch('/api/accounts')).json();
                const accounts = data.accounts || [];
                const container = document.getElementById('smtp-accounts-list');
                container.innerHTML = '';
                accounts.forEach(acc => {
                    container.innerHTML += '<div class="card mb-2"><div class="card-body"><strong>' + (acc.name || 'Account') + '</strong><br><small>' + (acc.email || '') + '</small></div></div>';
                });
            } catch (e) { console.error(e); }
        }

        async function loadWarmup() {
            try {
                const data = await (await fetch('/api/warmup')).json();
                const sessions = data.sessions || [];
                const container = document.getElementById('warmup-list');
                if (sessions.length === 0) { container.innerHTML = '<p class="text-muted">No active sessions</p>'; return; }
                sessions.forEach(s => {
                    container.innerHTML += '<div class="card mb-2"><div class="card-body"><strong>' + (s.email || 'Unknown') + '</strong> - Phase ' + (s.phase || 1) + '</div></div>';
                });
            } catch (e) { console.error(e); }
        }

        async function loadBounces() {
            try {
                const data = await (await fetch('/api/bounces')).json();
                const bounces = data.bounces || [];
                const container = document.getElementById('bounce-list');
                if (bounces.length === 0) { container.innerHTML = '<p class="text-muted">No bounces</p>'; return; }
                bounces.forEach(b => {
                    container.innerHTML += '<div class="alert alert-danger"><strong>' + (b.email || '') + '</strong><br><small>' + (b.message || '') + '</small></div>';
                });
            } catch (e) { console.error(e); }
        }

        // Template Editor Functions
        function insertTag(tag) {
            const editor = document.getElementById('template-editor-html');
            const snippets = {
                'h1': '<h1>Your Heading</h1>',
                'h2': '<h2>Your Subheading</h2>',
                'p': '<p>Your paragraph text here...</p>',
                'a': '<a href="https://example.com" style="color: #667eea;">Click Here</a>',
                'img': '<img src="IMAGE_URL" alt="Image" style="max-width: 100%;">',
                'button': '<a href="#" style="display: inline-block; padding: 12px 24px; background: #667eea; color: white; text-decoration: none; border-radius: 5px;">Button</a>'
            };
            if (snippets[tag]) {
                const start = editor.selectionStart;
                const end = editor.selectionEnd;
                editor.value = editor.value.substring(0, start) + snippets[tag] + editor.value.substring(end);
                editor.selectionStart = editor.selectionEnd = start + snippets[tag].length;
            }
        }

        function insertVariable() {
            const editor = document.getElementById('template-editor-html');
            const variables = ['$name', '$email', '$unsubscribe_url', '$company_name', '$subject'];
            const selected = prompt('Variable to insert:\\n' + variables.join('\\n'));
            if (selected && variables.includes(selected)) {
                const start = editor.selectionStart;
                editor.value = editor.value.substring(0, start) + selected + editor.value.substring(editor.selectionEnd);
            }
        }

        function formatHTML() {
            const editor = document.getElementById('template-editor-html');
            let html = editor.value;
            html = html.replace(/></g, '>\\n<');
            editor.value = html;
            showToast('HTML formatted!');
        }

        function insertImage(url) {
            const editor = document.getElementById('template-editor-html');
            const imgTag = '<img src="' + url + '" alt="Image" style="max-width: 100%;">';
            const start = editor.selectionStart;
            editor.value = editor.value.substring(0, start) + imgTag + editor.value.substring(editor.selectionEnd);
            showToast('Image tag inserted!');
        }

        function insertLink(url) {
            const editor = document.getElementById('template-editor-html');
            const linkTag = '<a href="' + url + '" style="color: #667eea;">Link</a>';
            const start = editor.selectionStart;
            editor.value = editor.value.substring(0, start) + linkTag + editor.value.substring(editor.selectionEnd);
            showToast('Link tag inserted!');
        }

        function updatePreview() {
            const html = document.getElementById('template-editor-html').value;
            document.getElementById('template-live-preview').innerHTML = html;
            showToast('Preview updated!');
        }

        async function saveTemplate() {
            const html = document.getElementById('template-editor-html').value;
            const name = prompt('Enter template name:');
            if (!name) return;
            showLoading();
            try {
                await (await fetch('/api/templates/create', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({name: name, html: html})
                })).json();
                showToast('Template saved!');
            } catch (e) { showToast('Failed', 'error'); }
            hideLoading();
        }

        async function editTemplate(name) {
            try {
                const data = await (await fetch('/api/templates?name=' + name)).json();
                if (data.template) {
                    document.getElementById('template-editor-html').value = data.template.html || '';
                    showPage('templates-editor');
                    showToast('Template loaded in editor');
                }
            } catch (e) { showToast('Failed', 'error'); }
        }

        // Email Sending Functions
        async function sendSingleEmail(e) {
            e.preventDefault();
            showLoading();
            const senderEmail = document.getElementById('single-sender-email').value;
            const senderPassword = document.getElementById('single-sender-password').value;
            const data = {
                to: document.getElementById('single-to').value,
                from_name: document.getElementById('single-from').value,
                subject: document.getElementById('single-subject').value,
                template: document.getElementById('single-template').value,
                content: document.getElementById('single-content').value,
                track_opens: document.getElementById('track-opens').checked,
                track_clicks: document.getElementById('track-clicks').checked
            };
            // Only include credentials if provided (server will use defaults otherwise)
            if (senderEmail) data.from_email = senderEmail;
            if (senderPassword) data.from_password = senderPassword;
            try {
                const r = await (await fetch('/api/send/single', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data)})).json();
                if (r.success) {
                    showToast(r.message || 'Email sent!');
                } else {
                    showToast(r.error || 'Failed to send', 'error');
                }
            } catch (e) { showToast('Failed: ' + e, 'error'); }
            hideLoading();
        }

        async function sendMultipleEmails(e) {
            e.preventDefault();
            showLoading();
            const recipients = document.getElementById('multiple-recipients').value.split('\\n').filter(r => r.trim());
            const data = {
                recipients: recipients,
                subject: document.getElementById('multiple-subject').value,
                template: document.getElementById('multiple-template').value
            };
            try {
                const r = await (await fetch('/api/send/multiple', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data)})).json();
                showToast('Queued ' + (r.recipients_count || recipients.length) + ' emails!');
            } catch (e) { showToast('Failed', 'error'); }
            hideLoading();
        }

        async function sendBulkEmail(e) {
            e.preventDefault();
            showLoading();
            const data = {
                template: document.getElementById('bulk-template').value,
                subject: document.getElementById('bulk-subject').value,
                batch_size: parseInt(document.getElementById('bulk-batch').value),
                delay_min: parseFloat(document.getElementById('bulk-delay-min').value),
                delay_max: parseFloat(document.getElementById('bulk-delay-max').value)
            };
            try {
                const r = await (await fetch('/api/send/bulk', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data)})).json();
                showToast(r.message || 'Campaign started!');
            } catch (e) { showToast('Failed', 'error'); }
            hideLoading();
        }

        async function scheduleCampaign(e) {
            e.preventDefault();
            showLoading();
            const data = {
                name: document.getElementById('schedule-name').value,
                template: document.getElementById('schedule-template').value,
                subject: document.getElementById('schedule-subject').value,
                scheduled_for: document.getElementById('schedule-datetime').value,
                sender_email: document.getElementById('schedule-sender').value,
                email_list: 'email_list.txt'
            };
            try {
                const r = await (await fetch('/api/campaigns/schedule', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data)})).json();
                showToast(r.message || 'Campaign scheduled!');
            } catch (e) { showToast('Failed', 'error'); }
            hideLoading();
        }

        // Template Functions
        async function createTemplate(e) {
            e.preventDefault();
            showLoading();
            const data = {
                name: document.getElementById('template-name').value,
                html: document.getElementById('template-html').value,
                subject: document.getElementById('template-subject').value
            };
            try {
                const r = await (await fetch('/api/templates/create', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data)})).json();
                showToast('Template created!');
                showPage('templates-browse');
            } catch (e) { showToast('Failed', 'error'); }
            hideLoading();
        }

        async function importTemplate(e) {
            e.preventDefault();
            showLoading();
            const data = {
                name: document.getElementById('import-name').value,
                html: document.getElementById('import-html').value,
                subject: document.getElementById('import-subject').value
            };
            try {
                const r = await (await fetch('/api/templates/import-html', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data)})).json();
                showToast('Template imported!');
                showPage('templates-browse');
            } catch (e) { showToast('Failed', 'error'); }
            hideLoading();
        }

        async function deleteTemplate(name) {
            if (!confirm('Delete template "' + name + '"?')) return;
            showLoading();
            try {
                await (await fetch('/api/templates/delete', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({name})})).json();
                showToast('Template deleted!');
                loadTemplates();
            } catch (e) { showToast('Failed', 'error'); }
            hideLoading();
        }

        async function customizeTemplate() {
            showLoading();
            const data = {
                name: document.getElementById('customize-template-select').value,
                colors: {
                    '#667eea': document.getElementById('customize-primary').value,
                    '#764ba2': document.getElementById('customize-secondary').value
                },
                content: {
                    'company_name': document.getElementById('customize-company').value,
                    'unsubscribe_url': document.getElementById('customize-unsubscribe').value
                }
            };
            try {
                const r = await (await fetch('/api/templates/customize', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data)})).json();
                document.getElementById('customize-result').innerHTML = '<div class="alert alert-success">Customization applied! HTML updated in preview.</div>';
            } catch (e) { showToast('Failed', 'error'); }
            hideLoading();
        }

        // Image Functions
        async function uploadImage() {
            const file = document.getElementById('image-upload').files[0];
            if (!file) return;
            showLoading();
            const reader = new FileReader();
            reader.onload = async function(e) {
                try {
                    const data = {name: file.name, data: e.target.result};
                    const r = await (await fetch('/api/images/upload', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data)})).json();
                    showToast('Image uploaded!');
                    loadImages();
                } catch (e) { showToast('Failed', 'error'); }
                hideLoading();
            };
            reader.readAsDataURL(file);
        }

        // Link Functions
        async function addTrackedLink(e) {
            e.preventDefault();
            showLoading();
            const data = {
                name: document.getElementById('link-name').value,
                url: document.getElementById('link-url').value
            };
            try {
                const r = await (await fetch('/api/links/add', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data)})).json();
                showToast('Link added!');
                loadLinks();
            } catch (e) { showToast('Failed', 'error'); }
            hideLoading();
        }

        // Email List Functions
        async function addEmail(e) {
            e.preventDefault();
            showLoading();
            const data = {email: document.getElementById('add-email-single').value};
            try {
                const r = await (await fetch('/api/emails/add', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data)})).json();
                showToast(r.message || 'Email added!');
                loadEmails();
            } catch (e) { showToast('Failed', 'error'); }
            hideLoading();
        }

        async function addMultipleEmails(e) {
            e.preventDefault();
            showLoading();
            const emails = document.getElementById('add-emails-multiple').value.split('\\n');
            let added = 0;
            for (const email of emails) {
                if (email.trim() && email.includes('@')) {
                    try { await (await fetch('/api/emails/add', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({email: email.trim()}) })).json(); added++; } catch (e) {}
                }
            }
            showToast('Added ' + added + ' emails!');
            loadEmails();
            hideLoading();
        }

        async function deleteEmail(email) {
            if (!confirm('Delete ' + email + '?')) return;
            showLoading();
            try {
                await (await fetch('/api/emails/delete', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({email})})).json();
                showToast('Email deleted!');
                loadEmails();
            } catch (e) { showToast('Failed', 'error'); }
            hideLoading();
        }

        async function cleanInvalidEmails() {
            showLoading();
            try {
                const r = await (await fetch('/api/emails/clean', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({}) })).json();
                showToast('Cleaned! Removed ' + (r.removed_invalid || 0) + ' invalid');
                loadEmails();
            } catch (e) { showToast('Failed', 'error'); }
            hideLoading();
        }

        async function dedupEmails() {
            showLoading();
            try {
                const r = await (await fetch('/api/emails/dedup', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({}) })).json();
                showToast('Deduplicated! Removed ' + (r.duplicates_removed || 0) + ' duplicates');
                loadEmails();
            } catch (e) { showToast('Failed', 'error'); }
            hideLoading();
        }

        // Other Functions
        async function checkDomain(e) {
            e.preventDefault();
            showLoading();
            const data = {domain: document.getElementById('domain-name').value, provider: 'gmail'};
            try {
                const r = await (await fetch('/api/domain/check', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data)})).json();
                document.getElementById('domain-results').innerHTML = '<pre>' + JSON.stringify(r.results, null, 2) + '</pre>';
            } catch (e) { showToast('Failed', 'error'); }
            hideLoading();
        }

        async function checkSpam(e) {
            e.preventDefault();
            showLoading();
            const data = {content: document.getElementById('spam-content').value, subject: document.getElementById('spam-subject').value};
            try {
                const r = await (await fetch('/api/spam/check', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data)})).json();
                document.getElementById('spam-results').innerHTML = '<pre>' + JSON.stringify(r, null, 2) + '</pre>';
            } catch (e) { showToast('Failed', 'error'); }
            hideLoading();
        }

        async function optinSubscribe(e) {
            e.preventDefault();
            showLoading();
            const data = {email: document.getElementById('optin-email').value};
            try {
                const r = await (await fetch('/api/optin/subscribe', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data)})).json();
                showToast(r.message || 'Subscribed!');
            } catch (e) { showToast('Failed', 'error'); }
            hideLoading();
        }

        async function createSignature(e) {
            e.preventDefault();
            showLoading();
            const data = {name: document.getElementById('sig-name').value, title: document.getElementById('sig-title').value, company: document.getElementById('sig-company').value};
            try {
                const r = await (await fetch('/api/signature/create', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data)})).json();
                document.getElementById('signature-result').innerHTML = '<div class="alert alert-info">' + (r.signature || '') + '</div>';
            } catch (e) { showToast('Failed', 'error'); }
            hideLoading();
        }

        async function saveSettings(e) {
            e.preventDefault();
            showLoading();
            const data = {
                smtp_server: document.getElementById('setting-smtp-server').value,
                smtp_port: parseInt(document.getElementById('setting-smtp-port').value),
                sender_email: document.getElementById('setting-sender-email').value,
                sender_name: document.getElementById('setting-sender-name').value
            };
            try {
                const r = await (await fetch('/api/settings/save', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data)})).json();
                showToast(r.message || 'Settings saved!');
            } catch (e) { showToast('Failed', 'error'); }
            hideLoading();
        }

        // Initialize
        let campaignChart = null;
        let statsPieChart = null;
        let dailyActivityChart = null;
        let bounceChart = null;
        let successRateChart = null;
        let resourceChart = null;

        async function loadDashboard() {
            try {
                const stats = await (await fetch('/api/stats')).json();
                document.getElementById('stat-campaigns').textContent = stats.total_campaigns || 0;
                document.getElementById('stat-sent').textContent = (stats.total_sent || 0).toLocaleString();
                document.getElementById('stat-emails').textContent = (stats.email_count || 0).toLocaleString();
                document.getElementById('stat-templates').textContent = (stats.template_count || 0).toLocaleString();
                
                // Load chart data
                loadDashboardCharts();
            } catch (e) { console.error(e); }
        }

        async function loadDashboardCharts() {
            try {
                const data = await (await fetch('/api/chart-data')).json();
                
                // Campaign Performance Chart (Bar)
                const ctx1 = document.getElementById('campaign-chart');
                if (ctx1) {
                    if (campaignChart) campaignChart.destroy();
                    campaignChart = new Chart(ctx1, {
                        type: 'bar',
                        data: {
                            labels: data.labels || [],
                            datasets: [{
                                label: 'Emails Sent',
                                data: data.sent_data || [],
                                backgroundColor: 'rgba(102, 126, 234, 0.8)',
                                borderColor: 'rgba(102, 126, 234, 1)',
                                borderWidth: 1
                            }, {
                                label: 'Success Rate %',
                                data: data.success_data || [],
                                type: 'line',
                                borderColor: 'rgba(67, 233, 123, 1)',
                                backgroundColor: 'rgba(67, 233, 123, 0.2)',
                                yAxisID: 'y1'
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            scales: {
                                y: { beginAtZero: true },
                                y1: { beginAtZero: true, max: 100, position: 'right' }
                            }
                        }
                    });
                }
                
                // Stats Pie Chart
                const ctx2 = document.getElementById('stats-pie-chart');
                if (ctx2) {
                    if (statsPieChart) statsPieChart.destroy();
                    statsPieChart = new Chart(ctx2, {
                        type: 'doughnut',
                        data: {
                            labels: ['Sent', 'Templates', 'Emails'],
                            datasets: [{
                                data: [
                                    data.summary?.total_sent || 0,
                                    data.summary?.template_count || 0,
                                    data.summary?.email_count || 0
                                ],
                                backgroundColor: [
                                    'rgba(102, 126, 234, 0.8)',
                                    'rgba(240, 147, 251, 0.8)',
                                    'rgba(67, 233, 123, 0.8)'
                                ]
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false
                        }
                    });
                }
                
                // Recent campaigns table
                const tbody = document.getElementById('recent-campaigns-body');
                if (tbody && data.campaigns) {
                    tbody.innerHTML = '';
                    data.campaigns.slice(0, 5).forEach(c => {
                        tbody.innerHTML += `<tr><td>${c.name || 'Campaign'}</td><td>${c.sent || 0}</td><td>${c.success_rate || 100}%</td></tr>`;
                    });
                }
            } catch (e) { console.error('Chart loading error:', e); }
        }

        async function loadAnalytics() {
            try {
                const data = await (await fetch('/api/analytics')).json();
                
                // Update stats
                document.getElementById('analytics-campaigns').textContent = data.summary?.total_campaigns || 0;
                document.getElementById('analytics-sent').textContent = (data.summary?.total_sent || 0).toLocaleString();
                document.getElementById('analytics-rate').textContent = (data.summary?.success_rate || 100) + '%';
                document.getElementById('analytics-templates').textContent = data.template_count || 0;
                
                // Daily Activity Chart (Line)
                const ctx1 = document.getElementById('daily-activity-chart');
                if (ctx1) {
                    if (dailyActivityChart) dailyActivityChart.destroy();
                    dailyActivityChart = new Chart(ctx1, {
                        type: 'line',
                        data: {
                            labels: data.days || ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                            datasets: [{
                                label: 'Emails Sent',
                                data: data.daily_sent || [0, 0, 0, 0, 0, 0, 0],
                                borderColor: 'rgba(102, 126, 234, 1)',
                                backgroundColor: 'rgba(102, 126, 234, 0.2)',
                                fill: true,
                                tension: 0.4
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false
                        }
                    });
                }
                
                // Bounce Chart (Doughnut)
                const ctx2 = document.getElementById('bounce-chart');
                if (ctx2) {
                    if (bounceChart) bounceChart.destroy();
                    bounceChart = new Chart(ctx2, {
                        type: 'doughnut',
                        data: {
                            labels: ['Hard Bounces', 'Soft Bounces', 'Delivered'],
                            datasets: [{
                                data: [
                                    data.bounce_stats?.hard_bounces || 0,
                                    data.bounce_stats?.soft_bounces || 0,
                                    (data.summary?.total_sent || 0) - (data.bounce_stats?.total || 0)
                                ],
                                backgroundColor: [
                                    'rgba(245, 87, 108, 0.8)',
                                    'rgba(255, 193, 7, 0.8)',
                                    'rgba(67, 233, 123, 0.8)'
                                ]
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false
                        }
                    });
                }
                
                // Success Rate Chart (Bar)
                const ctx3 = document.getElementById('success-rate-chart');
                if (ctx3) {
                    if (successRateChart) successRateChart.destroy();
                    successRateChart = new Chart(ctx3, {
                        type: 'bar',
                        data: {
                            labels: (data.campaigns || []).slice(0, 10).map(c => c.name || 'Campaign'),
                            datasets: [{
                                label: 'Success Rate %',
                                data: (data.campaigns || []).slice(0, 10).map(c => c.success_rate || 100),
                                backgroundColor: 'rgba(67, 233, 123, 0.8)',
                                borderColor: 'rgba(67, 233, 123, 1)',
                                borderWidth: 1
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            scales: { y: { beginAtZero: true, max: 100 } }
                        }
                    });
                }
                
                // Resource Distribution (Pie)
                const ctx4 = document.getElementById('resource-chart');
                if (ctx4) {
                    if (resourceChart) resourceChart.destroy();
                    resourceChart = new Chart(ctx4, {
                        type: 'pie',
                        data: {
                            labels: ['Emails', 'Templates', 'Campaigns'],
                            datasets: [{
                                data: [
                                    data.email_count || 0,
                                    data.template_count || 0,
                                    data.summary?.total_campaigns || 0
                                ],
                                backgroundColor: [
                                    'rgba(102, 126, 234, 0.8)',
                                    'rgba(240, 147, 251, 0.8)',
                                    'rgba(79, 172, 254, 0.8)'
                                ]
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false
                        }
                    });
                }
                
                // Campaigns Table
                const tbody = document.getElementById('campaigns-table-body');
                if (tbody && data.campaigns) {
                    tbody.innerHTML = '';
                    data.campaigns.forEach(c => {
                        const status = c.status || 'completed';
                        const statusClass = status === 'completed' ? 'success' : (status === 'failed' ? 'danger' : 'primary');
                        tbody.innerHTML += `<tr>
                            <td>${c.name || 'Campaign'}</td>
                            <td>${c.date || '-'}</td>
                            <td>${c.sent || 0}</td>
                            <td>${c.success_rate || 100}%</td>
                            <td>${c.bounces || 0}</td>
                            <td><span class="badge bg-${statusClass}">${status}</span></td>
                        </tr>`;
                    });
                }
            } catch (e) { console.error('Analytics loading error:', e); }
        }
    </script>
</body>
</html>'''