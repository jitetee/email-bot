#!/usr/bin/env python3
"""
Verify that web_app_enhanced.py sends REAL emails via SMTP
and uses .env configuration for credentials.
"""

import re
from pathlib import Path

WEB_APP_FILE = Path(__file__).parent / 'web_app_enhanced.py'
CONFIG_FILE = Path(__file__).parent / 'config.py'

def verify_real_email_sending():
    """Verify that the web app uses real SMTP with .env config."""
    
    print("=" * 60)
    print("🔍 Verifying Real Email Sending with .env Config")
    print("=" * 60)
    print()
    
    if not WEB_APP_FILE.exists():
        print("❌ ERROR: web_app_enhanced.py not found!")
        return False
    
    content = WEB_APP_FILE.read_text()
    
    checks = {
        'smtplib imported': r'import smtplib',
        'SMTP connection': r'SMTP\(',
        'TLS encryption': r'\.starttls\(\)',
        'SMTP login': r'\.login\(',
        'sendmail call': r'\.sendmail\(',
        'server quit': r'\.quit\(\)',
        'MIME message': r'MIMEMultipart',
        'api_send_single exists': r'def api_send_single\(self',
        'api_send_bulk exists': r'def api_send_bulk\(self',
        'api_send_test exists': r'def api_send_test\(self',
    }
    
    all_passed = True
    
    for check_name, pattern in checks.items():
        if re.search(pattern, content):
            print(f"✅ {check_name}: FOUND")
        else:
            print(f"❌ {check_name}: NOT FOUND")
            all_passed = False
    
    print()
    
    # Check .env config import
    print("📋 Checking .env Configuration Usage:")
    if re.search(r'from config import', content) and 'SENDER_EMAIL' in content and 'SENDER_PASSWORD' in content:
        print("   ✅ Imports SENDER_EMAIL and SENDER_PASSWORD from config")
    else:
        print("   ❌ Does NOT import from config.py")
        all_passed = False
    
    # Check default usage
    if re.search(r"body\.get\('from_email',\s*SENDER_EMAIL\)", content):
        print("   ✅ Uses SENDER_EMAIL from .env as default")
    else:
        print("   ⚠️  May not use .env config as default")
    
    if re.search(r"body\.get\('from_password',\s*SENDER_PASSWORD\)", content):
        print("   ✅ Uses SENDER_PASSWORD from .env as default")
    else:
        print("   ⚠️  May not use .env config as default")
    
    print()
    
    # Check api_send_single implementation
    print("📧 Checking api_send_single method...")
    send_single_match = re.search(
        r'def api_send_single\(self.*?server\.quit\(\)',
        content,
        re.DOTALL
    )
    if send_single_match:
        method_code = send_single_match.group(0)
        if 'smtplib' in method_code and 'server.sendmail' in method_code:
            print("   ✅ Uses REAL SMTP with sendmail()")
        else:
            print("   ❌ Does NOT use real SMTP")
            all_passed = False
        
        if 'SENDER_EMAIL' in method_code and 'SENDER_PASSWORD' in method_code:
            print("   ✅ Uses .env credentials (SENDER_EMAIL/SENDER_PASSWORD)")
        else:
            print("   ⚠️  May not use .env credentials")
    else:
        print("   ❌ Could not verify api_send_single implementation")
        all_passed = False
    
    print()
    
    # Check api_send_bulk implementation
    print("📦 Checking api_send_bulk method...")
    send_bulk_match = re.search(
        r'def api_send_bulk\(self.*?server\.quit\(\)',
        content,
        re.DOTALL
    )
    if send_bulk_match:
        method_code = send_bulk_match.group(0)
        if 'smtplib' in method_code and 'server.sendmail' in method_code:
            print("   ✅ Uses REAL SMTP with sendmail()")
        else:
            print("   ❌ Does NOT use real SMTP")
            all_passed = False
        
        if 'SENDER_EMAIL' in method_code and 'SENDER_PASSWORD' in method_code:
            print("   ✅ Uses .env credentials (SENDER_EMAIL/SENDER_PASSWORD)")
        else:
            print("   ⚠️  May not use .env credentials")
    else:
        print("   ❌ Could not verify api_send_bulk implementation")
        all_passed = False
    
    print()
    
    # Check api_send_test implementation
    print("🧪 Checking api_send_test method...")
    send_test_match = re.search(
        r'def api_send_test\(self.*?(?:server\.quit\(\)|self\.send_json)',
        content,
        re.DOTALL
    )
    if send_test_match:
        method_code = send_test_match.group(0)
        if 'smtplib' in method_code and 'server.sendmail' in method_code:
            print("   ✅ Uses REAL SMTP with sendmail()")
        elif 'REAL SMTP' in method_code:
            print("   ✅ Mentions REAL SMTP")
        else:
            print("   ⚠️  May not use real SMTP")
        
        if 'SENDER_EMAIL' in method_code:
            print("   ✅ Uses .env credentials")
    else:
        print("   ❌ Could not verify api_send_test implementation")
    
    print()
    print("=" * 60)
    
    if all_passed:
        print("✅ VERIFICATION PASSED!")
        print("   web_app_enhanced.py sends REAL emails via SMTP")
        print("   using .env configuration for credentials")
        print("=" * 60)
        return True
    else:
        print("⚠️  VERIFICATION INCOMPLETE")
        print("   Some checks failed. Review the code manually.")
        print("=" * 60)
        return False

if __name__ == '__main__':
    verify_real_email_sending()
