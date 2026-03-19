"""Domain Authentication Checker - Verify SPF, DKIM, DMARC records."""
import subprocess
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class DomainAuthChecker:
    """Check and validate domain authentication records for email deliverability."""

    def __init__(self):
        self.dns_resolver = self._check_dns_tools()

    def _check_dns_tools(self) -> str:
        """Check available DNS lookup tools."""
        # Try dig first (most reliable)
        try:
            result = subprocess.run(['dig', '-v'], capture_output=True, text=True)
            if result.returncode == 0:
                return 'dig'
        except (FileNotFoundError, Exception):
            pass

        # Try nslookup
        try:
            result = subprocess.run(['nslookup', '-v'], capture_output=True, text=True)
            if result.returncode == 0:
                return 'nslookup'
        except (FileNotFoundError, Exception):
            pass

        return None

    def query_dns(self, domain: str, record_type: str = 'TXT') -> List[str]:
        """
        Query DNS records for a domain.
        
        Args:
            domain: Domain to query
            record_type: DNS record type (TXT, MX, etc.)
        
        Returns:
            List of record values
        """
        if not self.dns_resolver:
            return self._query_dns_fallback(domain, record_type)

        results = []
        
        try:
            if self.dns_resolver == 'dig':
                cmd = ['dig', '+short', '-t', record_type, domain]
            else:  # nslookup
                cmd = ['nslookup', '-type=' + record_type, domain]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                output = result.stdout.strip()
                if output:
                    # Parse output based on tool
                    if self.dns_resolver == 'dig':
                        results = [line.strip('"') for line in output.split('\n') if line]
                    else:
                        # nslookup parsing
                        in_answer = False
                        for line in output.split('\n'):
                            if 'Non-authoritative answer' in line or 'Answer' in line:
                                in_answer = True
                            elif in_answer and line.strip() and not line.startswith('Server:'):
                                if record_type in line or '=' in line or 'text' in line.lower():
                                    results.append(line.strip('"').strip())
        except (subprocess.TimeoutExpired, Exception) as e:
            pass

        return results

    def _query_dns_fallback(self, domain: str, record_type: str = 'TXT') -> List[str]:
        """Fallback DNS query using Python's built-in methods."""
        # This is limited - recommends installing dig/nslookup
        return []

    def check_spf(self, domain: str) -> Dict:
        """
        Check SPF record for domain.
        
        SPF (Sender Policy Framework) specifies which servers can send email for your domain.
        """
        result = {
            'domain': domain,
            'has_spf': False,
            'record': None,
            'valid': False,
            'issues': [],
            'recommendations': [],
            'policy': None
        }

        txt_records = self.query_dns(domain, 'TXT')
        
        # Find SPF record
        spf_record = None
        for record in txt_records:
            if 'v=spf1' in record.lower():
                spf_record = record
                break

        if not spf_record:
            result['issues'].append("No SPF record found - emails may be marked as spam")
            result['recommendations'].append(
                f"Add SPF record: v=spf1 include:_spf.google.com ~all (for Gmail)"
            )
            return result

        result['has_spf'] = True
        result['record'] = spf_record

        # Validate SPF syntax
        if not spf_record.startswith('v=spf1'):
            result['issues'].append("SPF record doesn't start with v=spf1")
            return result

        result['valid'] = True

        # Check for common mechanisms
        mechanisms = spf_record.split()
        
        # Check policy qualifier
        if '~all' in mechanisms:
            result['policy'] = 'softfail'
        elif '-all' in mechanisms:
            result['policy'] = 'fail'
        elif '+all' in mechanisms:
            result['policy'] = 'pass'
            result['issues'].append("SPF policy '+all' is too permissive - anyone can send as your domain")
            result['recommendations'].append("Change '+all' to '~all' or '-all' for better security")
        elif '?all' in mechanisms:
            result['policy'] = 'neutral'
            result['issues'].append("SPF policy '?all' is neutral - provides no protection")

        # Check for includes
        includes = [m for m in mechanisms if m.startswith('include:')]
        if includes:
            result['includes'] = [i.replace('include:', '') for i in includes]
        
        # Check for common issues
        if len(spf_record) > 255:
            result['issues'].append("SPF record exceeds 255 characters - may cause DNS lookup issues")
        
        if spf_record.count('include:') > 10:
            result['issues'].append("Too many includes (>10) - exceeds DNS lookup limit")

        # Recommendations
        if not result['policy']:
            result['recommendations'].append("Add policy qualifier (~all or -all) at end of SPF record")

        return result

    def check_dkim(self, domain: str, selector: str = None) -> Dict:
        """
        Check DKIM record for domain.
        
        DKIM (DomainKeys Identified Mail) adds cryptographic signature to emails.
        """
        result = {
            'domain': domain,
            'has_dkim': False,
            'selector': selector,
            'record': None,
            'valid': False,
            'issues': [],
            'recommendations': []
        }

        # Common selectors to try if none provided
        selectors_to_try = [
            selector,  # Custom selector
            'google', 'google._domainkey',  # Gmail/Google Workspace
            'default', 'default._domainkey',  # Common default
            'mail', 'mail._domainkey',
            's1', 's1._domainkey',  # Common selector
            'k1', 'k1._domainkey',  # Another common selector
        ] if not selector else [selector, f"{selector}._domainkey"]

        # Try to find DKIM record
        for sel in selectors_to_try:
            if not sel:
                continue
            
            # Construct DKIM DNS name
            dkim_name = f"{sel}._domainkey.{domain}" if '_domainkey' not in sel else f"{sel}.{domain}"
            
            txt_records = self.query_dns(dkim_name, 'TXT')
            
            for record in txt_records:
                if 'v=DKIM1' in record or 'k=rsa' in record:
                    result['has_dkim'] = True
                    result['selector'] = sel
                    result['record'] = record
                    result['valid'] = True
                    result['dns_name'] = dkim_name
                    break
            
            if result['has_dkim']:
                break

        if not result['has_dkim']:
            result['issues'].append("No DKIM record found")
            result['recommendations'].append(
                "Set up DKIM with your email provider (Gmail, SendGrid, etc.)"
            )
            result['recommendations'].append(
                "Common selectors to check: google, default, mail, s1"
            )
        else:
            # Validate DKIM record structure
            if 'v=DKIM1' not in result['record']:
                result['issues'].append("DKIM record missing version tag (v=DKIM1)")
            
            if 'k=rsa' not in result['record'].lower() and 'p=' not in result['record']:
                result['issues'].append("DKIM record may be missing public key (p= tag)")

        return result

    def check_dmarc(self, domain: str) -> Dict:
        """
        Check DMARC record for domain.
        
        DMARC (Domain-based Message Authentication) tells receivers what to do 
        if SPF or DKIM fails.
        """
        result = {
            'domain': domain,
            'has_dmarc': False,
            'record': None,
            'valid': False,
            'policy': None,
            'issues': [],
            'recommendations': []
        }

        # DMARC record is at _dmarc.domain.com
        dmarc_name = f"_dmarc.{domain}"
        txt_records = self.query_dns(dmarc_name, 'TXT')

        # Find DMARC record
        dmarc_record = None
        for record in txt_records:
            if 'v=dmarc1' in record.lower():
                dmarc_record = record
                break

        if not dmarc_record:
            result['issues'].append("No DMARC record found")
            result['recommendations'].append(
                "Add DMARC record: v=DMARC1; p=none; rua=mailto:dmarc@yourdomain.com"
            )
            return result

        result['has_dmarc'] = True
        result['record'] = dmarc_record
        result['valid'] = True

        # Parse DMARC tags
        tags = {}
        for part in dmarc_record.split(';'):
            part = part.strip()
            if '=' in part:
                key, value = part.split('=', 1)
                tags[key.strip().lower()] = value.strip()

        # Check policy
        policy = tags.get('p', 'none')
        result['policy'] = policy
        
        policy_descriptions = {
            'none': 'Monitor only - no action taken on failures',
            'quarantine': 'Suspicious emails go to spam folder',
            'reject': 'Failed emails are rejected'
        }
        result['policy_description'] = policy_descriptions.get(policy, policy)

        # Check subdomain policy
        sp_policy = tags.get('sp', policy)
        result['subdomain_policy'] = sp_policy

        # Check reporting
        rua = tags.get('rua')  # Aggregate reports
        ruf = tags.get('ruf')  # Forensic reports
        result['aggregate_report_email'] = rua
        result['forensic_report_email'] = ruf

        # Validate and provide recommendations
        if policy == 'none':
            result['recommendations'].append(
                "Consider upgrading DMARC policy from 'none' to 'quarantine' or 'reject' after monitoring"
            )
        
        if not rua:
            result['recommendations'].append(
                "Add rua=mailto:dmarc-reports@yourdomain.com to receive DMARC reports"
            )

        if 'pct' in tags and tags['pct'] != '100':
            result['recommendations'].append(
                f"DMARC only applied to {tags['pct']}% of emails - consider setting pct=100"
            )

        return result

    def check_mx(self, domain: str) -> Dict:
        """Check MX records for domain."""
        result = {
            'domain': domain,
            'has_mx': False,
            'records': [],
            'issues': []
        }

        mx_records = self.query_dns(domain, 'MX')
        
        if not mx_records:
            result['issues'].append("No MX records found - domain cannot receive emails")
            return result

        result['has_mx'] = True
        
        for record in mx_records:
            # Parse MX record (priority + server)
            parts = record.split()
            if len(parts) >= 2:
                result['records'].append({
                    'priority': parts[0],
                    'server': parts[1]
                })
            else:
                result['records'].append({
                    'priority': 'N/A',
                    'server': record
                })

        return result

    def full_auth_check(self, domain: str, dkim_selector: str = None) -> Dict:
        """
        Perform complete domain authentication check.
        
        Returns comprehensive report of all authentication records.
        """
        return {
            'domain': domain,
            'checked_at': datetime.now().isoformat(),
            'spf': self.check_spf(domain),
            'dkim': self.check_dkim(domain, dkim_selector),
            'dmarc': self.check_dmarc(domain),
            'mx': self.check_mx(domain),
            'overall_score': 0,
            'deliverability_rating': 'UNKNOWN',
            'summary': []
        }

    def calculate_score(self, auth_report: Dict) -> Tuple[int, str]:
        """
        Calculate overall authentication score.
        
        Returns score (0-100) and rating.
        """
        score = 0
        issues = []

        # SPF scoring (max 30 points)
        spf = auth_report.get('spf', {})
        if spf.get('has_spf'):
            score += 15
            if spf.get('valid'):
                score += 10
            if spf.get('policy') in ['fail', 'softfail']:
                score += 5
            else:
                issues.append("SPF policy not strict enough")
        else:
            issues.append("Missing SPF record")

        # DKIM scoring (max 30 points)
        dkim = auth_report.get('dkim', {})
        if dkim.get('has_dkim'):
            score += 20
            if dkim.get('valid'):
                score += 10
            else:
                issues.append("DKIM record has issues")
        else:
            issues.append("Missing DKIM record")

        # DMARC scoring (max 30 points)
        dmarc = auth_report.get('dmarc', {})
        if dmarc.get('has_dmarc'):
            score += 15
            if dmarc.get('valid'):
                score += 10
            policy = dmarc.get('policy', 'none')
            if policy == 'reject':
                score += 5
            elif policy == 'quarantine':
                score += 3
            else:
                issues.append("DMARC policy is 'none' - consider 'quarantine' or 'reject'")
        else:
            issues.append("Missing DMARC record")

        # MX scoring (max 10 points)
        mx = auth_report.get('mx', {})
        if mx.get('has_mx'):
            score += 10
        else:
            issues.append("Missing MX records")

        # Determine rating
        if score >= 90:
            rating = 'EXCELLENT'
        elif score >= 70:
            rating = 'GOOD'
        elif score >= 50:
            rating = 'FAIR'
        elif score >= 30:
            rating = 'POOR'
        else:
            rating = 'VERY POOR'

        auth_report['overall_score'] = score
        auth_report['deliverability_rating'] = rating
        auth_report['issues'] = issues

        return score, rating

    def generate_setup_guide(self, domain: str, email_provider: str = 'gmail') -> str:
        """
        Generate DNS setup guide for domain.
        
        Args:
            domain: Domain to configure
            email_provider: Email provider (gmail, sendgrid, mailgun, etc.)
        """
        provider_configs = {
            'gmail': {
                'spf_include': '_spf.google.com',
                'dkim_selector': 'google',
                'setup_url': 'https://support.google.com/a/answer/174124'
            },
            'sendgrid': {
                'spf_include': 'sendgrid.net',
                'dkim_selector': 's1._domainkey',
                'setup_url': 'https://docs.sendgrid.com/ui/account-and-settings/how-to-set-up-domain-authentication'
            },
            'mailgun': {
                'spf_include': 'mailgun.org',
                'dkim_selector': 'k1._domainkey',
                'setup_url': 'https://documentation.mailgun.com/en/latest/user_manual.html#domain-verification'
            },
            'outlook': {
                'spf_include': 'spf.protection.outlook.com',
                'dkim_selector': 'selector1._domainkey',
                'setup_url': 'https://docs.microsoft.com/en-us/microsoft-365/admin/setup/add-domain'
            }
        }

        config = provider_configs.get(email_provider.lower(), provider_configs['gmail'])

        guide = f"""
# Domain Authentication Setup Guide for {domain}

## 1. SPF Record (Sender Policy Framework)

Add this TXT record to your DNS:

**Host/Name:** @{domain}
**Type:** TXT
**Value:** `v=spf1 include:{config['spf_include']} ~all`

This authorizes {email_provider} to send emails on behalf of your domain.

## 2. DKIM Record (DomainKeys Identified Mail)

1. Log in to your {email_provider} account
2. Navigate to email authentication settings
3. Generate DKIM keys for domain: {domain}
4. Add the provided DKIM TXT record to your DNS

**Host/Name:** {config['dkim_selector']}.{domain}
**Type:** TXT
**Value:** (provided by {email_provider})

Setup guide: {config['setup_url']}

## 3. DMARC Record (Domain-based Message Authentication)

Add this TXT record to your DNS:

**Host/Name:** _dmarc.{domain}
**Type:** TXT
**Value:** `v=DMARC1; p=none; rua=mailto:dmarc-reports@{domain}; pct=100`

Start with p=none to monitor, then upgrade to p=quarantine or p=reject.

## 4. Verify Setup

After adding records (may take 24-48 hours to propagate):

```bash
python domain_auth_checker.py {domain}
```

## Tips

- DNS changes can take 24-48 hours to propagate
- Test with a small email campaign first
- Monitor DMARC reports at dmarc-reports@{domain}
- Keep SPF record under 255 characters
- Use -all instead of ~all for stricter SPF after testing
"""
        return guide


def check_domain(domain: str, provider: str = 'gmail') -> Dict:
    """Convenience function to check domain authentication."""
    checker = DomainAuthChecker()
    report = checker.full_auth_check(domain)
    checker.calculate_score(report)
    return report


if __name__ == '__main__':
    import sys

    print("=" * 70)
    print("Domain Authentication Checker")
    print("SPF, DKIM, DMARC Verification")
    print("=" * 70)

    checker = DomainAuthChecker()

    if len(sys.argv) < 2:
        print("\nUsage: python domain_auth_checker.py <domain> [provider]")
        print("\nExamples:")
        print("  python domain_auth_checker.py gmail.com")
        print("  python domain_auth_checker.py company.com gmail")
        print("\nProviders: gmail, sendgrid, mailgun, outlook")
        print("\nNote: DNS lookup tools (dig/nslookup) recommended for best results")
        sys.exit(0)

    domain = sys.argv[1]
    provider = sys.argv[2] if len(sys.argv) > 2 else 'gmail'

    print(f"\nChecking authentication for: {domain}")
    print(f"Email provider: {provider}")
    print(f"DNS tool available: {checker.dns_resolver or 'None (limited results)'}")
    print("-" * 70)

    # Full check
    report = checker.full_auth_check(domain)
    score, rating = checker.calculate_score(report)

    # SPF
    spf = report['spf']
    print(f"\n{'='*70}")
    print("SPF (Sender Policy Framework)")
    print(f"{'='*70}")
    print(f"Status: {'✓ Found' if spf['has_spf'] else '✗ Missing'}")
    if spf['record']:
        print(f"Record: {spf['record'][:100]}{'...' if len(spf['record']) > 100 else ''}")
    print(f"Policy: {spf.get('policy', 'N/A')}")
    print(f"Valid: {'Yes' if spf['valid'] else 'No'}")
    if spf['issues']:
        print("Issues:")
        for issue in spf['issues']:
            print(f"  ✗ {issue}")
    if spf['recommendations']:
        print("Recommendations:")
        for rec in spf['recommendations']:
            print(f"  → {rec}")

    # DKIM
    dkim = report['dkim']
    print(f"\n{'='*70}")
    print("DKIM (DomainKeys Identified Mail)")
    print(f"{'='*70}")
    print(f"Status: {'✓ Found' if dkim['has_dkim'] else '✗ Missing'}")
    if dkim['record']:
        print(f"Selector: {dkim['selector']}")
        print(f"Record: {dkim['record'][:80]}{'...' if len(dkim['record']) > 80 else ''}")
    print(f"Valid: {'Yes' if dkim['valid'] else 'No'}")
    if dkim['issues']:
        print("Issues:")
        for issue in dkim['issues']:
            print(f"  ✗ {issue}")
    if dkim['recommendations']:
        print("Recommendations:")
        for rec in dkim['recommendations']:
            print(f"  → {rec}")

    # DMARC
    dmarc = report['dmarc']
    print(f"\n{'='*70}")
    print("DMARC (Domain-based Message Authentication)")
    print(f"{'='*70}")
    print(f"Status: {'✓ Found' if dmarc['has_dmarc'] else '✗ Missing'}")
    if dmarc['record']:
        print(f"Record: {dmarc['record']}")
    print(f"Policy: {dmarc.get('policy', 'N/A')} - {dmarc.get('policy_description', '')}")
    print(f"Subdomain Policy: {dmarc.get('subdomain_policy', 'N/A')}")
    if dmarc.get('aggregate_report_email'):
        print(f"Reports sent to: {dmarc['aggregate_report_email']}")
    print(f"Valid: {'Yes' if dmarc['valid'] else 'No'}")
    if dmarc['issues']:
        print("Issues:")
        for issue in dmarc['issues']:
            print(f"  ✗ {issue}")
    if dmarc['recommendations']:
        print("Recommendations:")
        for rec in dmarc['recommendations']:
            print(f"  → {rec}")

    # MX
    mx = report['mx']
    print(f"\n{'='*70}")
    print("MX (Mail Exchange)")
    print(f"{'='*70}")
    print(f"Status: {'✓ Found' if mx['has_mx'] else '✗ Missing'}")
    if mx['records']:
        print("Mail servers:")
        for rec in mx['records']:
            print(f"  Priority {rec['priority']}: {rec['server']}")

    # Overall
    print(f"\n{'='*70}")
    print("OVERALL ASSESSMENT")
    print(f"{'='*70}")
    print(f"Authentication Score: {score}/100")
    print(f"Deliverability Rating: {rating}")
    
    if report.get('issues'):
        print(f"\nCritical Issues ({len(report['issues'])}):")
        for issue in report['issues']:
            print(f"  ✗ {issue}")

    # Setup guide
    print(f"\n{'='*70}")
    print("SETUP GUIDE")
    print(f"{'='*70}")
    print(f"\nNeed help setting up authentication? Run:")
    print(f"  python domain_auth_checker.py {domain} {provider} --guide")

    print(f"\n{'='*70}\n")
