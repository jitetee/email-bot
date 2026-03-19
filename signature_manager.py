"""Email Signature Manager - Create and manage professional email signatures."""
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class SignatureManager:
    """Manage email signatures with multiple templates."""

    def __init__(self, data_file: Path = None):
        self.data_file = data_file or Path(__file__).parent / 'data' / 'signatures.json'
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Create data file if it doesn't exist."""
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.data_file.exists():
            self._save_data({'signatures': [], 'default': None})

    def _load_data(self) -> Dict:
        """Load data from JSON file."""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {'signatures': [], 'default': None}

    def _save_data(self, data: Dict):
        """Save data to JSON file."""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)

    def create_signature(self, name: str, info: Dict) -> Dict:
        """
        Create a new email signature.

        Args:
            name: Signature name
            info: Signature info (name, title, company, phone, email, website, etc.)

        Returns:
            Created signature data
        """
        data = self._load_data()

        signature = {
            'id': f"sig_{len(data['signatures']) + 1}",
            'name': name,
            'info': info,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }

        data['signatures'].append(signature)

        # Set as default if first signature
        if len(data['signatures']) == 1:
            data['default'] = signature['id']

        self._save_data(data)
        return signature

    def get_signature(self, signature_id: str) -> Optional[Dict]:
        """Get signature by ID."""
        data = self._load_data()
        for sig in data['signatures']:
            if sig['id'] == signature_id:
                return sig
        return None

    def get_default(self) -> Optional[Dict]:
        """Get default signature."""
        data = self._load_data()
        if not data.get('default'):
            return None
        return self.get_signature(data['default'])

    def set_default(self, signature_id: str) -> bool:
        """Set default signature."""
        data = self._load_data()
        if self.get_signature(signature_id):
            data['default'] = signature_id
            self._save_data(data)
            return True
        return False

    def update_signature(self, signature_id: str, info: Dict) -> Optional[Dict]:
        """Update signature info."""
        data = self._load_data()
        for sig in data['signatures']:
            if sig['id'] == signature_id:
                sig['info'] = info
                sig['updated_at'] = datetime.now().isoformat()
                self._save_data(data)
                return sig
        return None

    def delete_signature(self, signature_id: str) -> bool:
        """Delete signature."""
        data = self._load_data()
        original_count = len(data['signatures'])
        data['signatures'] = [s for s in data['signatures'] if s['id'] != signature_id]

        if len(data['signatures']) < original_count:
            if data['default'] == signature_id:
                data['default'] = data['signatures'][0]['id'] if data['signatures'] else None
            self._save_data(data)
            return True
        return False

    def generate_html(self, signature_id: str = None, template: str = 'modern') -> str:
        """
        Generate HTML signature.

        Args:
            signature_id: Signature ID (uses default if None)
            template: Template style (modern, minimal, professional, colorful)

        Returns:
            HTML signature string
        """
        if signature_id:
            sig = self.get_signature(signature_id)
        else:
            sig = self.get_default()

        if not sig:
            return "<p>No signature configured</p>"

        info = sig['info']
        templates = {
            'modern': self._modern_template(info),
            'minimal': self._minimal_template(info),
            'professional': self._professional_template(info),
            'colorful': self._colorful_template(info)
        }

        return templates.get(template, self._modern_template(info))

    def _modern_template(self, info: Dict) -> str:
        """Modern signature template."""
        return f"""
<table cellpadding="0" cellspacing="0" border="0" style="font-family: Arial, sans-serif; font-size: 14px; line-height: 1.6; color: #333;">
    <tr>
        <td style="padding-right: 20px;">
            <strong style="font-size: 18px; color: #2c3e50;">{info.get('name', '')}</strong><br>
            <span style="color: #7f8c8d;">{info.get('title', '')}</span>
        </td>
    </tr>
    <tr>
        <td style="padding-top: 10px;">
            <table cellpadding="0" cellspacing="0" border="0">
                {'<tr><td style="padding: 2px 0;">📧 <a href="mailto:' + info.get('email', '') + '" style="color: #3498db; text-decoration: none;">' + info.get('email', '') + '</a></td></tr>' if info.get('email') else ''}
                {'<tr><td style="padding: 2px 0;">📱 ' + info.get('phone', '') + '</td></tr>' if info.get('phone') else ''}
                {'<tr><td style="padding: 2px 0;">🌐 <a href="' + info.get('website', '') + '" style="color: #3498db; text-decoration: none;">' + info.get('website', '') + '</a></td></tr>' if info.get('website') else ''}
                {'<tr><td style="padding: 2px 0;">🏢 ' + info.get('company', '') + '</td></tr>' if info.get('company') else ''}
                {'<tr><td style="padding: 2px 0;">📍 ' + info.get('address', '') + '</td></tr>' if info.get('address') else ''}
            </table>
        </td>
    </tr>
    {'<tr><td style="padding-top: 15px;"><img src="' + info.get('logo', '') + '" alt="Logo" style="max-height: 40px;"></td></tr>' if info.get('logo') else ''}
    <tr>
        <td style="padding-top: 15px; border-top: 2px solid #3498db; padding-top: 10px;">
            <table cellpadding="0" cellspacing="0" border="0">
                <tr>
                    {('<td style="padding-right: 10px;"><a href="' + info.get('linkedin', '') + '" style="text-decoration: none;">LinkedIn</a></td>') if info.get('linkedin') else ''}
                    {('<td style="padding-right: 10px;"><a href="' + info.get('twitter', '') + '" style="text-decoration: none;">Twitter</a></td>') if info.get('twitter') else ''}
                    {('<td><a href="' + info.get('facebook', '') + '" style="text-decoration: none;">Facebook</a></td>') if info.get('facebook') else ''}
                </tr>
            </table>
        </td>
    </tr>
</table>
""".strip()

    def _minimal_template(self, info: Dict) -> str:
        """Minimal signature template."""
        parts = [
            f"<strong>{info.get('name', '')}</strong>",
            info.get('title', ''),
            info.get('company', ''),
        ]
        
        contact = []
        if info.get('email'):
            contact.append(f'<a href="mailto:{info["email"]}">{info["email"]}</a>')
        if info.get('phone'):
            contact.append(info['phone'])
        if info.get('website'):
            contact.append(f'<a href="{info["website"]}">{info["website"]}</a>')

        return f"""
<div style="font-family: Arial, sans-serif; font-size: 13px; color: #555; line-height: 1.5;">
    <p style="margin: 0;">{' | '.join(filter(None, parts))}</p>
    <p style="margin: 5px 0 0 0; color: #888;">{' • '.join(contact)}</p>
</div>
""".strip()

    def _professional_template(self, info: Dict) -> str:
        """Professional signature template."""
        return f"""
<table cellpadding="0" cellspacing="0" border="0" style="font-family: Georgia, serif; font-size: 14px; color: #444;">
    <tr>
        <td style="border-left: 3px solid #1a5276; padding-left: 15px;">
            <strong style="font-size: 16px; color: #1a5276;">{info.get('name', '')}</strong><br>
            <em>{info.get('title', '')}</em><br>
            <strong>{info.get('company', '')}</strong>
        </td>
    </tr>
    <tr>
        <td style="padding-left: 15px; padding-top: 10px; font-size: 12px; color: #666;">
            {info.get('email', '')} | {info.get('phone', '')}<br>
            {info.get('website', '')} | {info.get('address', '')}
        </td>
    </tr>
</table>
""".strip()

    def _colorful_template(self, info: Dict) -> str:
        """Colorful signature template."""
        return f"""
<table cellpadding="0" cellspacing="0" border="0" style="font-family: Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px;">
    <tr>
        <td style="color: white;">
            <strong style="font-size: 20px;">{info.get('name', '')}</strong><br>
            <span style="opacity: 0.9;">{info.get('title', '')}</span>
        </td>
    </tr>
    <tr>
        <td style="padding-top: 15px; color: white; opacity: 0.9; font-size: 13px;">
            📧 {info.get('email', '')}<br>
            📱 {info.get('phone', '')}<br>
            🌐 {info.get('website', '')}<br>
            🏢 {info.get('company', '')}
        </td>
    </tr>
</table>
""".strip()

    def list_signatures(self) -> List[Dict]:
        """List all signatures."""
        data = self._load_data()
        return data['signatures']

    def export_signature(self, signature_id: str, output_file: Path) -> bool:
        """Export signature to HTML file."""
        sig = self.get_signature(signature_id)
        if not sig:
            return False

        html = self.generate_html(signature_id)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Email Signature - {sig['name']}</title>
</head>
<body style="padding: 20px; background: #f5f5f5;">
    <div style="background: white; padding: 20px; border-radius: 10px; display: inline-block;">
        {html}
    </div>
</body>
</html>""")
        return True


if __name__ == '__main__':
    import sys

    manager = SignatureManager()

    print("=" * 60)
    print("Email Signature Manager")
    print("=" * 60)

    if len(sys.argv) < 2:
        print("\nUsage: python signature_manager.py <command> [args]")
        print("\nCommands:")
        print("  create <name>                    - Create new signature")
        print("  list                             - List all signatures")
        print("  get <id>                         - Get signature details")
        print("  default [id]                     - Get/Set default signature")
        print("  generate [id] [template]         - Generate HTML")
        print("  export <id> <file>               - Export to HTML file")
        print("  delete <id>                      - Delete signature")
        print("\nTemplates: modern, minimal, professional, colorful")
        sys.exit(0)

    command = sys.argv[1]

    if command == 'create':
        print("\n=== Create Signature ===")
        name = input("Signature name: ")
        info = {}
        print("\nEnter signature details (press Enter to skip):")
        info['name'] = input("  Full name: ")
        info['title'] = input("  Job title: ")
        info['company'] = input("  Company: ")
        info['email'] = input("  Email: ")
        info['phone'] = input("  Phone: ")
        info['website'] = input("  Website: ")
        info['address'] = input("  Address: ")
        info['linkedin'] = input("  LinkedIn URL: ")
        info['twitter'] = input("  Twitter URL: ")
        info['logo'] = input("  Logo URL: ")

        # Remove empty fields
        info = {k: v for k, v in info.items() if v}

        sig = manager.create_signature(name, info)
        print(f"\n✓ Signature created: {sig['id']}")

    elif command == 'list':
        sigs = manager.list_signatures()
        default = manager.get_default()
        default_id = default['id'] if default else None

        print(f"\nSignatures ({len(sigs)}):")
        for sig in sigs:
            marker = " (default)" if sig['id'] == default_id else ""
            print(f"  {sig['id']}: {sig['name']}{marker}")

    elif command == 'get' and len(sys.argv) > 2:
        sig = manager.get_signature(sys.argv[2])
        if sig:
            print(f"\nSignature: {sig['name']}")
            print(f"ID: {sig['id']}")
            print(f"Created: {sig['created_at']}")
            print("\nInfo:")
            for key, value in sig['info'].items():
                print(f"  {key}: {value}")
        else:
            print("Signature not found")

    elif command == 'default':
        if len(sys.argv) > 2:
            if manager.set_default(sys.argv[2]):
                print(f"✓ Default signature set to {sys.argv[2]}")
            else:
                print("Signature not found")
        else:
            default = manager.get_default()
            if default:
                print(f"Default signature: {default['name']} ({default['id']})")
            else:
                print("No default signature set")

    elif command == 'generate':
        sig_id = sys.argv[2] if len(sys.argv) > 2 else None
        template = sys.argv[3] if len(sys.argv) > 3 else 'modern'
        html = manager.generate_html(sig_id, template)
        print("\n" + "=" * 60)
        print("Generated HTML Signature:")
        print("=" * 60)
        print(html)
        print("=" * 60)

    elif command == 'export' and len(sys.argv) > 3:
        if manager.export_signature(sys.argv[2], Path(sys.argv[3])):
            print(f"✓ Signature exported to {sys.argv[3]}")
        else:
            print("Signature not found")

    elif command == 'delete' and len(sys.argv) > 2:
        if manager.delete_signature(sys.argv[2]):
            print(f"✓ Signature deleted")
        else:
            print("Signature not found")

    else:
        print(f"Unknown command: {command}")
