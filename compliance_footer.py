"""Compliance Footer Generator - CAN-SPAM and GDPR compliant email footers."""
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime


class ComplianceFooterGenerator:
    """Generate legally compliant email footers for CAN-SPAM and GDPR."""

    def __init__(self, company_info: Dict = None):
        self.company_info = company_info or {
            'name': 'Your Company',
            'address': '123 Business St, City, State 12345',
            'email': 'contact@yourcompany.com',
            'phone': '+1-555-123-4567',
            'website': 'https://yourcompany.com'
        }

    def generate_can_spam_footer(self, unsubscribe_url: str, company_info: Dict = None) -> str:
        """
        Generate CAN-SPAM compliant footer.
        
        Requirements:
        - Clear unsubscribe mechanism
        - Physical mailing address
        - Accurate sender information
        """
        info = company_info or self.company_info
        
        footer = f"""
<table role="presentation" style="width:100%;border-top:1px solid #e0e0e0;margin-top:30px;padding-top:20px;">
    <tr>
        <td align="center" style="font-family:Arial,sans-serif;font-size:12px;color:#666666;">
            <p style="margin:0 0 10px 0;">
                <strong>{info['name']}</strong><br>
                {info['address']}
            </p>
            <p style="margin:0 0 10px 0;">
                Email: <a href="mailto:{info['email']}" style="color:#666666;text-decoration:underline;">{info['email']}</a>
                {f' | Phone: {info["phone"]}' if info.get('phone') else ''}
            </p>
            <p style="margin:0 0 10px 0;">
                <a href="{unsubscribe_url}" style="color:#666666;text-decoration:underline;">Unsubscribe</a>
                {f' | <a href="{info["website"]}" style="color:#666666;text-decoration:underline;">Visit Website</a>' if info.get('website') else ''}
            </p>
            <p style="margin:10px 0 0 0;font-size:11px;">
                You received this email because you opted in to receive emails from {info['name']}.
            </p>
        </td>
    </tr>
</table>
""".strip()
        
        return footer

    def generate_gdpr_footer(self, unsubscribe_url: str, privacy_policy_url: str, 
                            company_info: Dict = None) -> str:
        """
        Generate GDPR compliant footer.
        
        Requirements:
        - Clear consent reminder
        - Privacy policy link
        - Data controller information
        - Easy unsubscribe
        """
        info = company_info or self.company_info
        
        footer = f"""
<table role="presentation" style="width:100%;border-top:1px solid #e0e0e0;margin-top:30px;padding-top:20px;">
    <tr>
        <td align="center" style="font-family:Arial,sans-serif;font-size:12px;color:#666666;">
            <p style="margin:0 0 10px 0;">
                <strong>{info['name']}</strong><br>
                {info['address']}
            </p>
            <p style="margin:0 0 10px 0;">
                You're receiving this because you consented to receive emails from {info['name']}.
            </p>
            <p style="margin:0 0 10px 0;">
                <a href="{unsubscribe_url}" style="color:#ffffff;background-color:#666666;padding:8px 16px;text-decoration:none;border-radius:4px;display:inline-block;margin:5px;">Unsubscribe</a>
            </p>
            <p style="margin:0 0 10px 0;">
                <a href="{privacy_policy_url}" style="color:#666666;text-decoration:underline;">Privacy Policy</a>
                {f' | <a href="{info["website"]}" style="color:#666666;text-decoration:underline;">Website</a>' if info.get('website') else ''}
            </p>
            <p style="margin:10px 0 0 0;font-size:11px;">
                Data Controller: {info['name']} ({info['email']})<br>
                We respect your privacy and will never share your information.
            </p>
        </td>
    </tr>
</table>
""".strip()
        
        return footer

    def generate_minimal_footer(self, unsubscribe_url: str, company_info: Dict = None) -> str:
        """Generate a simple, minimal compliant footer."""
        info = company_info or self.company_info
        
        footer = f"""
<table role="presentation" style="width:100%;border-top:1px solid #e0e0e0;margin-top:20px;padding-top:15px;">
    <tr>
        <td align="center" style="font-family:Arial,sans-serif;font-size:11px;color:#999999;">
            <p style="margin:0 0 5px 0;">{info['name']} | {info['address']}</p>
            <p style="margin:0;">
                <a href="{unsubscribe_url}" style="color:#999999;text-decoration:underline;">Unsubscribe</a>
            </p>
        </td>
    </tr>
</table>
""".strip()
        
        return footer

    def generate_plain_text_footer(self, unsubscribe_url: str, company_info: Dict = None) -> str:
        """Generate plain text footer for text-only emails."""
        info = company_info or self.company_info
        
        lines = [
            "",
            "--",
            info['name'],
            info['address'],
            f"Email: {info['email']}",
        ]
        
        if info.get('phone'):
            lines.append(f"Phone: {info['phone']}")
        
        lines.extend([
            "",
            f"Unsubscribe: {unsubscribe_url}",
            f"Website: {info.get('website', 'N/A')}",
            "",
            "You received this email because you opted in to receive emails from us."
        ])
        
        return "\n".join(lines)

    def generate_full_compliance_package(self, subject: str, unsubscribe_url: str,
                                        privacy_policy_url: str = None,
                                        company_info: Dict = None) -> Dict:
        """
        Generate complete compliance package for an email.
        
        Returns dict with all required elements.
        """
        info = company_info or self.company_info
        
        return {
            'html_footer': self.generate_can_spam_footer(unsubscribe_url, info),
            'gdpr_footer': self.generate_gdpr_footer(
                unsubscribe_url, 
                privacy_policy_url or f"{info.get('website', '')}/privacy",
                info
            ),
            'plain_text_footer': self.generate_plain_text_footer(unsubscribe_url, info),
            'headers': {
                'List-Unsubscribe': f"<{unsubscribe_url}>",
                'List-Unsubscribe-Post': "List-Unsubscribe=One-Click",
                'List-ID': f"{info['name']} <{info['email']}>",
                'List-Help': f"<{privacy_policy_url or info.get('website', '')}/contact>",
            },
            'compliance_checklist': {
                'physical_address': bool(info.get('address')),
                'unsubscribe_link': bool(unsubscribe_url),
                'sender_identified': bool(info.get('name')),
                'privacy_policy': bool(privacy_policy_url),
                'can_spam_compliant': bool(info.get('address')) and bool(unsubscribe_url),
                'gdpr_ready': bool(unsubscribe_url) and bool(privacy_policy_url)
            }
        }

    def validate_compliance(self, email_content: str, footer_included: bool = True) -> Dict:
        """
        Validate email for compliance requirements.
        
        Returns dict with compliance status and missing elements.
        """
        issues = []
        warnings = []

        # Check for physical address
        if not any(keyword in email_content.lower() for keyword in ['street', 'st', 'avenue', 'ave', 'road', 'rd']):
            issues.append("Missing physical mailing address (CAN-SPAM requirement)")

        # Check for unsubscribe link
        if 'unsubscribe' not in email_content.lower():
            issues.append("Missing unsubscribe mechanism (CAN-SPAM requirement)")

        # Check for sender identification
        if not any(keyword in email_content.lower() for keyword in ['from', 'sender', 'company']):
            warnings.append("Consider adding clear sender identification")

        # Check subject line for deception
        if any(keyword in email_content.lower() for keyword in ['urgent', 'act now', 'immediate']):
            warnings.append("Subject may be perceived as urgent/pressuring")

        return {
            'can_spam_compliant': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'recommendation': "Fix issues before sending to ensure legal compliance" if issues else "Email appears compliant"
        }


def generate_footer(template_type: str = 'can_spam', **kwargs) -> str:
    """Convenience function to generate footer."""
    generator = ComplianceFooterGenerator(kwargs.get('company_info'))
    
    if template_type == 'can_spam':
        return generator.generate_can_spam_footer(kwargs.get('unsubscribe_url', '#'))
    elif template_type == 'gdpr':
        return generator.generate_gdpr_footer(
            kwargs.get('unsubscribe_url', '#'),
            kwargs.get('privacy_policy_url', '#')
        )
    elif template_type == 'minimal':
        return generator.generate_minimal_footer(kwargs.get('unsubscribe_url', '#'))
    elif template_type == 'plain_text':
        return generator.generate_plain_text_footer(kwargs.get('unsubscribe_url', '#'))
    else:
        return generator.generate_can_spam_footer(kwargs.get('unsubscribe_url', '#'))


if __name__ == '__main__':
    import sys

    print("=" * 60)
    print("Compliance Footer Generator")
    print("=" * 60)

    # Demo company info
    demo_company = {
        'name': 'Acme Corporation',
        'address': '123 Business Ave, Suite 100, New York, NY 10001',
        'email': 'hello@acme.com',
        'phone': '+1-555-987-6543',
        'website': 'https://acme.com'
    }

    generator = ComplianceFooterGenerator(demo_company)

    print("\n--- CAN-SPAM Footer (HTML) ---\n")
    can_spam = generator.generate_can_spam_footer(
        unsubscribe_url="https://acme.com/unsubscribe?email=user@example.com"
    )
    print(can_spam)

    print("\n\n--- GDPR Footer (HTML) ---\n")
    gdpr = generator.generate_gdpr_footer(
        unsubscribe_url="https://acme.com/unsubscribe?email=user@example.com",
        privacy_policy_url="https://acme.com/privacy"
    )
    print(gdpr)

    print("\n\n--- Plain Text Footer ---\n")
    plain_text = generator.generate_plain_text_footer(
        unsubscribe_url="https://acme.com/unsubscribe?email=user@example.com"
    )
    print(plain_text)

    print("\n\n--- Full Compliance Package ---\n")
    package = generator.generate_full_compliance_package(
        subject="Special Offer",
        unsubscribe_url="https://acme.com/unsubscribe",
        privacy_policy_url="https://acme.com/privacy",
        company_info=demo_company
    )
    
    print("Compliance Checklist:")
    for item, status in package['compliance_checklist'].items():
        print(f"  {'✓' if status else '✗'} {item.replace('_', ' ').title()}")

    print("\nEmail Headers:")
    for header, value in package['headers'].items():
        print(f"  {header}: {value}")

    # Validate sample email
    print("\n\n--- Compliance Validation ---\n")
    sample_email = """
    <html>
    <body>
        <h1>Special Offer!</h1>
        <p>Check out our latest products.</p>
        <p>From Acme Corporation</p>
    </body>
    </html>
    """
    
    validation = generator.validate_compliance(sample_email)
    print(f"CAN-SPAM Compliant: {'Yes' if validation['can_spam_compliant'] else 'No'}")
    if validation['issues']:
        print("\nIssues:")
        for issue in validation['issues']:
            print(f"  ✗ {issue}")
    if validation['warnings']:
        print("\nWarnings:")
        for warning in validation['warnings']:
            print(f"  ⚠ {warning}")

    print(f"\n{'='*60}\n")
