"""Template Preview - Open HTML templates in browser."""
import webbrowser
import tempfile
import os
from pathlib import Path
from datetime import datetime


class TemplatePreview:
    """Preview email templates in a web browser."""
    
    def __init__(self, template_dir: Path):
        self.template_dir = template_dir
    
    def get_template_files(self, template_name: str) -> dict:
        """Get paths for template files."""
        return {
            'html': self.template_dir / f"{template_name}.html",
            'subject': self.template_dir / f"{template_name}_subject.txt"
        }
    
    def list_templates(self) -> list:
        """List all available templates."""
        templates = []
        for f in self.template_dir.glob("*.html"):
            if not f.name.endswith('_subject.txt'):
                templates.append(f.stem)
        return sorted(templates)
    
    def preview(self, template_name: str, variables: dict = None) -> bool:
        """
        Open template in default browser.
        
        Args:
            template_name: Name of template (without extension)
            variables: Dict of template variables to substitute
            
        Returns:
            True if successful
        """
        files = self.get_template_files(template_name)
        
        if not files['html'].exists():
            print(f"Template not found: {template_name}")
            return False
        
        # Read HTML
        with open(files['html'], 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Apply variables if provided
        if variables:
            for key, value in variables.items():
                html_content = html_content.replace(f"${{{key}}}", str(value))
                html_content = html_content.replace(f"${{{key.lower()}}}", str(value))
        
        # Read subject if exists
        subject = ""
        if files['subject'].exists():
            with open(files['subject'], 'r', encoding='utf-8') as f:
                subject = f.read().strip()
        
        # Create enhanced preview with subject display
        enhanced_html = self._create_preview_wrapper(html_content, subject, template_name)
        
        # Save to temp file
        temp_file = tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.html',
            delete=False,
            encoding='utf-8'
        )
        temp_file.write(enhanced_html)
        temp_file.close()
        
        # Open in browser
        try:
            webbrowser.open(f'file://{temp_file.name}')
            print(f"✓ Preview opened in browser: {template_name}")
            print(f"  Subject: {subject}")
            print(f"  Temp file: {temp_file.name}")
            return True
        except Exception as e:
            print(f"Error opening browser: {e}")
            return False
    
    def _create_preview_wrapper(self, html_content: str, subject: str, template_name: str) -> str:
        """Wrap email HTML with preview controls."""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Email Preview: {template_name}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #1a1a2e;
            min-height: 100vh;
            padding: 20px;
        }}
        .preview-container {{
            max-width: 800px;
            margin: 0 auto;
        }}
        .preview-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px 10px 0 0;
            margin-bottom: 0;
        }}
        .preview-header h1 {{
            font-size: 1.5rem;
            margin-bottom: 10px;
        }}
        .preview-meta {{
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
            font-size: 0.9rem;
            opacity: 0.9;
        }}
        .preview-meta span {{
            display: flex;
            align-items: center;
            gap: 5px;
        }}
        .subject-preview {{
            background: #16213e;
            color: #eee;
            padding: 15px 20px;
            border-left: 4px solid #667eea;
            margin: 0;
        }}
        .subject-label {{
            color: #667eea;
            font-weight: bold;
            margin-right: 10px;
        }}
        .email-wrapper {{
            background: white;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            border-radius: 0 0 10px 10px;
            overflow: hidden;
        }}
        .controls {{
            background: #0f0f23;
            padding: 15px 20px;
            margin-bottom: 20px;
            border-radius: 10px;
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            align-items: center;
        }}
        .controls button {{
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 0.9rem;
            transition: background 0.2s;
        }}
        .controls button:hover {{
            background: #5a6fd6;
        }}
        .controls button.secondary {{
            background: #333;
        }}
        .controls .info {{
            color: #aaa;
            font-size: 0.85rem;
            margin-left: auto;
        }}
        .view-toggle {{
            display: flex;
            gap: 5px;
        }}
        .view-toggle button {{
            background: #333;
        }}
        .view-toggle button.active {{
            background: #667eea;
        }}
        @media (max-width: 600px) {{
            .preview-header h1 {{ font-size: 1.2rem; }}
            .preview-meta {{ flex-direction: column; gap: 5px; }}
            .controls {{ flex-direction: column; }}
            .controls .info {{ margin-left: 0; }}
        }}
    </style>
</head>
<body>
    <div class="preview-container">
        <div class="controls">
            <strong style="color: #667eea;">📧 Email Preview</strong>
            <div class="view-toggle">
                <button onclick="toggleView('desktop')" id="btn-desktop" class="active">🖥️ Desktop</button>
                <button onclick="toggleView('mobile')" id="btn-mobile">📱 Mobile</button>
            </div>
            <button class="secondary" onclick="printPreview()">🖨️ Print</button>
            <button class="secondary" onclick="copyHtml()">📋 Copy HTML</button>
            <span class="info">Template: {template_name} | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</span>
        </div>
        
        <div class="preview-header">
            <h1>📨 Email Template Preview</h1>
            <div class="preview-meta">
                <span>📝 <strong>Subject:</strong> {subject}</span>
                <span>📁 <strong>Template:</strong> {template_name}.html</span>
                <span>📐 <strong>Size:</strong> ~{len(html_content)} bytes</span>
            </div>
        </div>
        
        <div class="subject-preview">
            <span class="subject-label">Subject:</span>
            <span>{subject}</span>
        </div>
        
        <div class="email-wrapper" id="email-container">
            {html_content}
        </div>
    </div>
    
    <script>
        function toggleView(view) {{
            const container = document.getElementById('email-container');
            const btnDesktop = document.getElementById('btn-desktop');
            const btnMobile = document.getElementById('btn-mobile');
            
            if (view === 'mobile') {{
                container.style.maxWidth = '400px';
                container.style.margin = '0 auto';
                btnMobile.classList.add('active');
                btnDesktop.classList.remove('active');
            }} else {{
                container.style.maxWidth = '100%';
                btnDesktop.classList.add('active');
                btnMobile.classList.remove('active');
            }}
        }}
        
        function printPreview() {{
            const content = document.getElementById('email-container').innerHTML;
            const printWindow = window.open('', '_blank');
            printWindow.document.write('<html><head><title>Print</title></head><body>' + content + '</body></html>');
            printWindow.document.close();
            printWindow.print();
        }}
        
        function copyHtml() {{
            const html = document.getElementById('email-container').innerHTML;
            navigator.clipboard.writeText(html).then(() => {{
                alert('HTML copied to clipboard!');
            }}).catch(err => {{
                console.error('Failed to copy:', err);
            }});
        }}
    </script>
</body>
</html>
"""
    
    def preview_with_variables(self, template_name: str, recipient_email: str = "user@example.com") -> bool:
        """Preview template with sample variables."""
        variables = {
            'name': recipient_email.split('@')[0],
            'email': recipient_email,
            'company': 'Your Company',
            'link': '#',
            'unsubscribe_link': '#',
            'current_date': datetime.now().strftime('%B %d, %Y'),
            'year': datetime.now().year
        }
        return self.preview(template_name, variables)


if __name__ == '__main__':
    import sys
    
    template_dir = Path(__file__).parent / 'templates'
    previewer = TemplatePreview(template_dir)
    
    print("=" * 60)
    print("Template Preview")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        template_name = sys.argv[1]
        
        # Check if template exists
        files = previewer.get_template_files(template_name)
        if not files['html'].exists():
            print(f"Template not found: {template_name}")
            print("\nAvailable templates:")
            for t in previewer.list_templates():
                print(f"  - {t}")
            sys.exit(1)
        
        # Show subject
        if files['subject'].exists():
            with open(files['subject'], 'r') as f:
                subject = f.read().strip()
            print(f"Subject: {subject}")
        
        # Preview
        confirm = input(f"\nOpen '{template_name}' in browser? (y/n): ")
        if confirm.lower() == 'y':
            previewer.preview_with_variables(template_name)
    else:
        print("\nAvailable templates:")
        for t in previewer.list_templates():
            files = previewer.get_template_files(t)
            subject = ""
            if files['subject'].exists():
                with open(files['subject'], 'r') as f:
                    subject = f.read().strip()[:50]
            print(f"  - {t:20} | {subject}")
        
        print("\nUsage: python template_preview.py <template_name>")
        print("Example: python template_preview.py modern_promo")
