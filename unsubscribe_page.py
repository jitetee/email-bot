"""Unsubscribe Page Generator - Create beautiful unsubscribe landing pages."""
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import hashlib


class UnsubscribePageGenerator:
    """Generate unsubscribe landing pages with multiple templates."""

    def __init__(self, pages_dir: Path = None):
        self.pages_dir = pages_dir or Path(__file__).parent / 'unsubscribe_pages'
        self.config_file = Path(__file__).parent / 'data' / 'unsubscribe_config.json'
        self._ensure_dirs_exist()

    def _ensure_dirs_exist(self):
        """Create directories if they don't exist."""
        self.pages_dir.mkdir(parents=True, exist_ok=True)
        self.config_file.parent.mkdir(parents=True, exist_ok=True)

    def _load_config(self) -> Dict:
        """Load configuration."""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {
                'company_name': 'Your Company',
                'company_email': 'contact@company.com',
                'company_address': '123 Business St, City, State 12345',
                'logo_url': '',
                'brand_color': '#667eea',
                'pages': []
            }

    def _save_config(self, config: Dict):
        """Save configuration."""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, default=str)

    def generate_page(self, email: str = None, template: str = 'modern', 
                     config_override: Dict = None) -> str:
        """
        Generate unsubscribe page HTML.

        Args:
            email: Pre-fill email (optional)
            template: Template style
            config_override: Override config values

        Returns:
            Complete HTML page
        """
        config = self._load_config()
        if config_override:
            config.update(config_override)

        templates = {
            'modern': self._modern_template(config, email),
            'minimal': self._minimal_template(config, email),
            'friendly': self._friendly_template(config, email),
            'professional': self._professional_template(config, email)
        }

        return templates.get(template, self._modern_template(config, email))

    def _modern_template(self, config: Dict, email: str) -> str:
        """Modern unsubscribe page template."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Unsubscribe | {config['company_name']}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px; }}
        .container {{ background: white; border-radius: 20px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); max-width: 500px; width: 100%; overflow: hidden; }}
        .header {{ background: {config['brand_color']}; color: white; padding: 40px 30px; text-align: center; }}
        .header h1 {{ font-size: 28px; margin-bottom: 10px; }}
        .header p {{ opacity: 0.9; font-size: 15px; }}
        .content {{ padding: 40px 30px; }}
        .form-group {{ margin-bottom: 25px; }}
        label {{ display: block; margin-bottom: 8px; font-weight: 600; color: #333; font-size: 14px; }}
        input[type="email"] {{ width: 100%; padding: 15px; border: 2px solid #e0e0e0; border-radius: 10px; font-size: 16px; transition: border-color 0.3s; }}
        input[type="email"]:focus {{ outline: none; border-color: {config['brand_color']}; }}
        .options {{ background: #f8f9fa; border-radius: 10px; padding: 20px; margin-bottom: 25px; }}
        .option {{ display: flex; align-items: flex-start; margin-bottom: 15px; }}
        .option:last-child {{ margin-bottom: 0; }}
        .option input {{ margin-right: 12px; margin-top: 4px; }}
        .option label {{ font-weight: normal; color: #555; font-size: 14px; line-height: 1.5; }}
        .btn {{ width: 100%; padding: 15px; background: {config['brand_color']}; color: white; border: none; border-radius: 10px; font-size: 16px; font-weight: 600; cursor: pointer; transition: opacity 0.3s; }}
        .btn:hover {{ opacity: 0.9; }}
        .btn-secondary {{ background: #6c757d; margin-top: 10px; }}
        .footer {{ text-align: center; padding: 20px; background: #f8f9fa; font-size: 12px; color: #888; }}
        .success {{ display: none; text-align: center; padding: 40px 30px; }}
        .success-icon {{ font-size: 60px; color: #28a745; margin-bottom: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>👋 We're Sad to See You Go</h1>
            <p>Manage your email preferences</p>
        </div>

        <div class="content" id="unsubscribeForm">
            <form id="unsubscribeFormEl" onsubmit="handleUnsubscribe(event)">
                <div class="form-group">
                    <label for="email">Email Address</label>
                    <input type="email" id="email" name="email" value="{email or ''}" required placeholder="your@email.com">
                </div>

                <div class="options">
                    <label style="margin-bottom: 15px; display: block;">Choose an option:</label>
                    
                    <div class="option">
                        <input type="radio" id="unsubscribe_all" name="preference" value="unsubscribe_all" checked>
                        <label for="unsubscribe_all"><strong>Unsubscribe from all emails</strong><br>No more marketing emails. You'll still receive transactional emails.</label>
                    </div>

                    <div class="option">
                        <input type="radio" id="reduce" name="preference" value="reduce">
                        <label for="reduce"><strong>Reduce frequency</strong><br>Send me fewer emails (weekly digest instead of daily).</label>
                    </div>

                    <div class="option">
                        <input type="radio" id="pause" name="preference" value="pause">
                        <label for="pause"><strong>Pause for 30 days</strong><br>Take a break and come back later.</label>
                    </div>
                </div>

                <button type="submit" class="btn">Confirm Unsubscribe</button>
                <button type="button" class="btn btn-secondary" onclick="window.close()">Cancel</button>
            </form>
        </div>

        <div class="success" id="successMessage">
            <div class="success-icon">✓</div>
            <h2 style="margin-bottom: 15px;">You've Been Unsubscribed</h2>
            <p style="color: #666; line-height: 1.6;">We're sorry to see you go. You won't receive marketing emails from us anymore.</p>
            <p style="margin-top: 20px; font-size: 13px; color: #888;">This process may take up to 48 hours to complete.</p>
        </div>

        <div class="footer">
            <p>{config['company_name']}</p>
            <p>{config['company_address']}</p>
            <p><a href="mailto:{config['company_email']}" style="color: #888;">{config['company_email']}</a></p>
        </div>
    </div>

    <script>
        function handleUnsubscribe(e) {{
            e.preventDefault();
            const email = document.getElementById('email').value;
            const preference = document.querySelector('input[name="preference"]:checked').value;
            
            // Store in localStorage for demo
            localStorage.setItem('unsubscribed', JSON.stringify({{ email, preference, date: new Date().toISOString() }}));
            
            // Show success message
            document.getElementById('unsubscribeForm').style.display = 'none';
            document.getElementById('successMessage').style.display = 'block';
            
            // In production, you would send this to your server
            console.log('Unsubscribe:', {{ email, preference }});
        }}
    </script>
</body>
</html>"""

    def _minimal_template(self, config: Dict, email: str) -> str:
        """Minimal unsubscribe page template."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Unsubscribe</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 400px; margin: 50px auto; padding: 20px; }}
        h1 {{ font-size: 24px; margin-bottom: 10px; }}
        p {{ color: #666; margin-bottom: 30px; }}
        input[type="email"] {{ width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 5px; margin-bottom: 20px; font-size: 16px; }}
        .options {{ margin-bottom: 25px; }}
        .option {{ margin-bottom: 12px; }}
        .option label {{ cursor: pointer; }}
        button {{ width: 100%; padding: 12px; background: #333; color: white; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; }}
        .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #888; text-align: center; }}
    </style>
</head>
<body>
    <h1>Unsubscribe</h1>
    <p>Sorry to see you go. Manage your preferences below.</p>

    <form onsubmit="alert('Unsubscribed!'); return false;">
        <input type="email" value="{email or ''}" placeholder="your@email.com" required>
        
        <div class="options">
            <div class="option">
                <input type="radio" id="all" name="pref" checked>
                <label for="all">Unsubscribe from all emails</label>
            </div>
            <div class="option">
                <input type="radio" id="reduce" name="pref">
                <label for="reduce">Reduce email frequency</label>
            </div>
        </div>

        <button type="submit">Confirm</button>
    </form>

    <div class="footer">
        <p>{config['company_name']}</p>
        <p>{config['company_email']}</p>
    </div>
</body>
</html>"""

    def _friendly_template(self, config: Dict, email: str) -> str:
        """Friendly unsubscribe page template."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>We'll Miss You! | {config['company_name']}</title>
    <style>
        body {{ font-family: 'Comic Sans MS', cursive, sans-serif; background: #fff5f5; min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px; }}
        .container {{ background: white; border-radius: 30px; box-shadow: 0 10px 40px rgba(0,0,0,0.1); max-width: 450px; width: 100%; padding: 40px; text-align: center; }}
        .emoji {{ font-size: 80px; margin-bottom: 20px; }}
        h1 {{ color: {config['brand_color']}; font-size: 26px; margin-bottom: 15px; }}
        p {{ color: #666; line-height: 1.6; margin-bottom: 25px; }}
        input[type="email"] {{ width: 100%; padding: 15px; border: 3px solid #f0f0f0; border-radius: 15px; font-size: 16px; margin-bottom: 20px; }}
        .btn {{ background: {config['brand_color']}; color: white; border: none; padding: 15px 40px; border-radius: 25px; font-size: 16px; cursor: pointer; margin: 10px; }}
        .btn-cancel {{ background: #ccc; }}
        .options {{ text-align: left; background: #f8f9fa; border-radius: 15px; padding: 20px; margin: 20px 0; }}
        .option {{ margin-bottom: 15px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="emoji">😢</div>
        <h1>We'll Miss You!</h1>
        <p>Is it something we said? Before you go, let us know your preferences.</p>

        <form onsubmit="alert('Thanks for letting us know! 💙'); return false;">
            <input type="email" value="{email or ''}" placeholder="your@email.com" required>
            
            <div class="options">
                <div class="option">
                    <input type="radio" id="bye" name="pref" checked>
                    <label for="bye"><strong>Bye for now!</strong> - Unsubscribe me from everything</label>
                </div>
                <div class="option">
                    <input type="radio" id="less" name="pref">
                    <label for="less"><strong>Slow down</strong> - Send me fewer emails</label>
                </div>
                <div class="option">
                    <input type="radio" id="break" name="pref">
                    <label for="break"><strong>Take a break</strong> - Pause for 30 days</label>
                </div>
            </div>

            <button type="submit" class="btn">Confirm</button>
            <button type="button" class="btn btn-cancel" onclick="window.close()">Stay</button>
        </form>
    </div>
</body>
</html>"""

    def _professional_template(self, config: Dict, email: str) -> str:
        """Professional unsubscribe page template."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Email Preferences | {config['company_name']}</title>
    <style>
        body {{ font-family: Georgia, serif; background: #f5f5f5; min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px; }}
        .container {{ background: white; border: 1px solid #ddd; max-width: 500px; width: 100%; }}
        .header {{ background: #1a5276; color: white; padding: 30px; border-bottom: 4px solid #b7950b; }}
        .header h1 {{ font-size: 24px; margin: 0; }}
        .content {{ padding: 30px; }}
        table {{ width: 100%; border-collapse: collapse; margin-bottom: 25px; }}
        td {{ padding: 12px 0; border-bottom: 1px solid #eee; }}
        input[type="email"] {{ width: 100%; padding: 10px; border: 1px solid #ddd; font-size: 14px; }}
        .btn {{ background: #1a5276; color: white; border: none; padding: 12px 30px; font-size: 14px; cursor: pointer; }}
        .footer {{ background: #f8f9fa; padding: 20px; font-size: 11px; color: #666; border-top: 1px solid #ddd; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Email Preferences</h1>
            <p style="margin: 10px 0 0 0; opacity: 0.9; font-size: 14px;">Manage your subscription</p>
        </div>

        <div class="content">
            <form onsubmit="alert('Preferences updated'); return false;">
                <table>
                    <tr>
                        <td><label for="email">Email Address</label></td>
                    </tr>
                    <tr>
                        <td><input type="email" id="email" value="{email or ''}" required></td>
                    </tr>
                </table>

                <table>
                    <tr>
                        <td><input type="radio" name="pref" value="unsubscribe" checked></td>
                        <td><strong>Unsubscribe from all marketing emails</strong></td>
                    </tr>
                    <tr>
                        <td><input type="radio" name="pref" value="reduce"></td>
                        <td>Reduce email frequency (weekly digest)</td>
                    </tr>
                    <tr>
                        <td><input type="radio" name="pref" value="pause"></td>
                        <td>Pause subscriptions for 30 days</td>
                    </tr>
                </table>

                <button type="submit" class="btn">Update Preferences</button>
            </form>
        </div>

        <div class="footer">
            <p><strong>{config['company_name']}</strong></p>
            <p>{config['company_address']}</p>
            <p>{config['company_email']}</p>
        </div>
    </div>
</body>
</html>"""

    def save_page(self, filename: str, template: str = 'modern', email: str = None):
        """Save unsubscribe page to file."""
        html = self.generate_page(email, template)
        filepath = self.pages_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        return filepath

    def update_config(self, **kwargs):
        """Update configuration."""
        config = self._load_config()
        config.update(kwargs)
        self._save_config(config)
        return config


if __name__ == '__main__':
    import sys

    generator = UnsubscribePageGenerator()

    print("=" * 60)
    print("Unsubscribe Page Generator")
    print("=" * 60)

    if len(sys.argv) < 2:
        print("\nUsage: python unsubscribe_page.py <command> [args]")
        print("\nCommands:")
        print("  generate [template] [email]  - Generate page (preview)")
        print("  save <filename> [template]   - Save page to file")
        print("  config <key> <value>         - Update configuration")
        print("  show-config                  - Show current config")
        print("\nTemplates: modern, minimal, friendly, professional")
        sys.exit(0)

    command = sys.argv[1]

    if command == 'generate':
        template = sys.argv[2] if len(sys.argv) > 2 else 'modern'
        email = sys.argv[3] if len(sys.argv) > 3 else None
        html = generator.generate_page(email, template)
        print(f"\nGenerated {template} template:")
        print("=" * 60)
        print(html[:500] + "...")
        print("=" * 60)

    elif command == 'save':
        filename = sys.argv[2] if len(sys.argv) > 2 else 'unsubscribe.html'
        template = sys.argv[3] if len(sys.argv) > 3 else 'modern'
        filepath = generator.save_page(filename, template)
        print(f"✓ Page saved to: {filepath}")

    elif command == 'config':
        if len(sys.argv) > 3:
            key = sys.argv[2]
            value = sys.argv[3]
            config = generator.update_config(**{key: value})
            print(f"✓ Updated {key} = {value}")
        else:
            print("Usage: python unsubscribe_page.py config <key> <value>")

    elif command == 'show-config':
        config = generator._load_config()
        print("\nCurrent Configuration:")
        print("-" * 40)
        for key, value in config.items():
            if key != 'pages':
                print(f"  {key}: {value}")
        print("-" * 40)

    else:
        print(f"Unknown command: {command}")
