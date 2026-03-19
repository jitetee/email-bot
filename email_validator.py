"""Email validation and verification utilities."""
import re
import socket
import dns.resolver
from typing import Tuple, Optional
from pathlib import Path


class EmailValidator:
    """Validate email addresses with multiple checks."""
    
    # Common disposable email domains
    DISPOSABLE_DOMAINS = {
        'tempmail.com', 'throwaway.com', 'guerrillamail.com', 'mailinator.com',
        '10minutemail.com', 'fakeinbox.com', 'trashmail.com', 'temp-mail.org'
    }
    
    # Role-based emails (often bounce)
    ROLE_PREFIXES = {
        'admin', 'support', 'info', 'sales', 'contact', 'help', 'noreply',
        'no-reply', 'postmaster', 'webmaster', 'hostmaster', 'abuse', 'billing'
    }
    
    def __init__(self):
        self.email_pattern = re.compile(
            r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        )
    
    def validate_syntax(self, email: str) -> bool:
        """Check if email has valid syntax."""
        return bool(self.email_pattern.match(email))
    
    def validate_domain(self, email: str) -> Tuple[bool, str]:
        """Check if domain exists and has MX records."""
        try:
            domain = email.split('@')[1].lower()
            
            # Check for disposable domains
            if domain in self.DISPOSABLE_DOMAINS:
                return False, "Disposable email domain"
            
            # Check MX records
            try:
                mx_records = dns.resolver.resolve(domain, 'MX')
                if mx_records:
                    return True, "Valid domain with MX records"
            except dns.resolver.NoAnswer:
                pass
            except dns.resolver.NXDOMAIN:
                return False, "Domain does not exist"
            except Exception:
                pass
            
            # Fallback: Check A record
            try:
                socket.gethostbyname(domain)
                return True, "Domain exists (no MX, has A record)"
            except socket.gaierror:
                return False, "Domain cannot be resolved"
                
        except IndexError:
            return False, "Invalid email format"
        
        return True, "Domain appears valid"
    
    def is_role_based(self, email: str) -> bool:
        """Check if email is role-based (admin@, support@, etc.)."""
        try:
            prefix = email.split('@')[0].lower()
            return prefix in self.ROLE_PREFIXES
        except IndexError:
            return False
    
    def is_disposable(self, email: str) -> bool:
        """Check if email is from a disposable provider."""
        try:
            domain = email.split('@')[1].lower()
            return domain in self.DISPOSABLE_DOMAINS
        except IndexError:
            return False
    
    def validate_full(self, email: str, check_dns: bool = True) -> dict:
        """
        Perform full email validation.
        
        Returns dict with:
            - valid: bool
            - email: str
            - syntax_valid: bool
            - domain_valid: bool
            - is_disposable: bool
            - is_role_based: bool
            - risk_score: int (0-100, lower is better)
            - message: str
        """
        result = {
            'valid': True,
            'email': email,
            'syntax_valid': False,
            'domain_valid': False,
            'is_disposable': False,
            'is_role_based': False,
            'risk_score': 0,
            'message': ''
        }
        
        # Check syntax
        result['syntax_valid'] = self.validate_syntax(email)
        if not result['syntax_valid']:
            result['valid'] = False
            result['risk_score'] = 100
            result['message'] = 'Invalid email syntax'
            return result
        
        # Check if disposable
        result['is_disposable'] = self.is_disposable(email)
        if result['is_disposable']:
            result['risk_score'] += 50
        
        # Check if role-based
        result['is_role_based'] = self.is_role_based(email)
        if result['is_role_based']:
            result['risk_score'] += 20
        
        # Check domain
        if check_dns:
            domain_valid, domain_msg = self.validate_domain(email)
            result['domain_valid'] = domain_valid
            if not domain_valid:
                result['valid'] = False
                result['risk_score'] = 100
                result['message'] = domain_msg
                return result
        
        # Calculate final risk score
        if result['risk_score'] >= 70:
            result['valid'] = False
            result['message'] = f'High risk email (score: {result["risk_score"]})'
        elif result['risk_score'] >= 40:
            result['message'] = f'Medium risk email (score: {result["risk_score"]}) - Use with caution'
        else:
            result['message'] = f'Valid email (score: {result["risk_score"]})'
        
        return result
    
    def validate_list(self, file_path: Path, check_dns: bool = False) -> dict:
        """
        Validate all emails in a list file.
        
        Returns dict with statistics and lists of valid/invalid emails.
        """
        if not file_path.exists():
            return {'error': f'File not found: {file_path}'}
        
        results = {
            'total': 0,
            'valid': 0,
            'invalid': 0,
            'risky': 0,
            'valid_emails': [],
            'invalid_emails': [],
            'risky_emails': [],
            'details': []
        }
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                email = line.strip()
                if not email or email.startswith('#'):
                    continue
                
                results['total'] += 1
                validation = self.validate_full(email, check_dns=check_dns)
                results['details'].append(validation)
                
                if validation['valid'] and validation['risk_score'] < 40:
                    results['valid'] += 1
                    results['valid_emails'].append(email)
                elif validation['risk_score'] >= 40:
                    results['risky'] += 1
                    results['risky_emails'].append({
                        'email': email,
                        'score': validation['risk_score'],
                        'message': validation['message']
                    })
                else:
                    results['invalid'] += 1
                    results['invalid_emails'].append({
                        'email': email,
                        'reason': validation['message']
                    })
        
        return results


def quick_validate(email: str) -> bool:
    """Quick syntax-only validation."""
    validator = EmailValidator()
    return validator.validate_syntax(email)


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        email = sys.argv[1]
        validator = EmailValidator()
        result = validator.validate_full(email)
        
        print(f"\n{'='*50}")
        print(f"Email Validation Report: {email}")
        print(f"{'='*50}")
        print(f"Valid: {result['valid']}")
        print(f"Syntax OK: {result['syntax_valid']}")
        print(f"Domain OK: {result['domain_valid']}")
        print(f"Disposable: {result['is_disposable']}")
        print(f"Role-based: {result['is_role_based']}")
        print(f"Risk Score: {result['risk_score']}/100")
        print(f"Message: {result['message']}")
        print(f"{'='*50}\n")
    else:
        print("Usage: python email_validator.py <email>")
        print("Example: python email_validator.py test@gmail.com")
