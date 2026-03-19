"""Email template system with HTML support."""
from pathlib import Path
from string import Template
from typing import Optional


class EmailTemplate:
    """Handles email template loading and rendering."""
    
    def __init__(self, template_dir: Path):
        self.template_dir = template_dir
    
    def load_template(self, name: str) -> dict:
        """Load a template by name.
        
        Args:
            name: Template name (without .html extension)
            
        Returns:
            dict with 'subject' and 'body' keys
        """
        html_file = self.template_dir / f"{name}.html"
        subject_file = self.template_dir / f"{name}_subject.txt"
        
        # Load HTML body
        if html_file.exists():
            with open(html_file, 'r', encoding='utf-8') as f:
                body = f.read()
        else:
            body = self._get_default_template()
        
        # Load subject
        if subject_file.exists():
            with open(subject_file, 'r', encoding='utf-8') as f:
                subject = f.read().strip()
        else:
            subject = "Special Offer Just for You!"
        
        return {'subject': subject, 'body': body}
    
    def render(self, template_name: str, variables: dict) -> dict:
        """Render a template with variables.
        
        Args:
            template_name: Name of the template
            variables: Dict of variables to substitute ($variable_name)
            
        Returns:
            dict with rendered 'subject' and 'body'
        """
        template = self.load_template(template_name)
        
        # Use string Template for safe substitution
        safe_template = Template(template['body'])
        safe_subject = Template(template['subject'])
        
        try:
            rendered_body = safe_template.safe_substitute(variables)
            rendered_subject = safe_subject.safe_substitute(variables)
        except Exception:
            rendered_body = template['body']
            rendered_subject = template['subject']
        
        return {'subject': rendered_subject, 'body': rendered_body}
    
    def _get_default_template(self) -> str:
        """Return default promotional email HTML."""
        return """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; }
        .container { background: #f4f4f4; padding: 20px; border-radius: 10px; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
        .content { background: white; padding: 30px; }
        .promo-image { width: 100%; max-width: 500px; height: auto; border-radius: 8px; margin: 20px 0; }
        .cta-button { display: inline-block; background: #667eea; color: white; padding: 15px 40px; text-decoration: none; border-radius: 25px; margin: 20px 0; font-weight: bold; }
        .footer { background: #333; color: white; padding: 20px; text-align: center; border-radius: 0 0 10px 10px; font-size: 12px; }
        .highlight { color: #667eea; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 Special Promotion!</h1>
        </div>
        <div class="content">
            <p>Hi there,</p>
            <p>We have an <span class="highlight">exclusive offer</span> just for you!</p>
            
            <img src="https://via.placeholder.com/500x250/667eea/ffffff?text=Special+Offer" alt="Promotion" class="promo-image">
            
            <p>Don't miss out on this amazing opportunity. Click below to learn more:</p>
            
            <center>
                <a href="https://example.com" class="cta-button">Claim Your Offer</a>
            </center>
            
            <p>Best regards,<br><strong>Your Company Team</strong></p>
        </div>
        <div class="footer">
            <p>&copy; 2026 Your Company. All rights reserved.</p>
            <p>You received this email because you subscribed to our newsletter.</p>
            <p><a href="#" style="color: #aaa;">Unsubscribe</a></p>
        </div>
    </div>
</body>
</html>"""
    
    def save_template(self, name: str, subject: str, body: str) -> None:
        """Save a custom template.
        
        Args:
            name: Template name
            subject: Email subject line
            body: HTML body content
        """
        html_file = self.template_dir / f"{name}.html"
        subject_file = self.template_dir / f"{name}_subject.txt"
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(body)
        
        with open(subject_file, 'w', encoding='utf-8') as f:
            f.write(subject)
    
    def list_templates(self) -> list:
        """List available templates."""
        templates = []
        for f in self.template_dir.glob("*.html"):
            name = f.stem
            if not name.endswith("_subject"):
                templates.append(name)
        return templates
