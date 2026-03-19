"""Email List Manager - Add, remove, validate, import, deduplicate emails."""
import csv
import json
from pathlib import Path
from typing import List, Optional, Tuple
from datetime import datetime

from email_validator import EmailValidator


class EmailListManager:
    """Manage email lists with validation and deduplication."""
    
    def __init__(self, list_file: Path):
        self.list_file = list_file
        self.validator = EmailValidator()
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Create the email list file if it doesn't exist."""
        self.list_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.list_file.exists():
            self.list_file.touch()
    
    def load_emails(self) -> List[str]:
        """Load all emails from the list file."""
        if not self.list_file.exists():
            return []
        
        emails = []
        with open(self.list_file, 'r', encoding='utf-8') as f:
            for line in f:
                email = line.strip()
                if email and not email.startswith('#') and '@' in email:
                    emails.append(email)
        return emails
    
    def save_emails(self, emails: List[str]):
        """Save emails to the list file."""
        with open(self.list_file, 'w', encoding='utf-8') as f:
            f.write(f"# Email List - Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            for email in emails:
                f.write(f"{email}\n")
    
    def add_email(self, email: str, validate: bool = True) -> Tuple[bool, str]:
        """
        Add a single email to the list.
        
        Args:
            email: Email address to add
            validate: Whether to validate the email first
            
        Returns:
            Tuple of (success, message)
        """
        email = email.strip()
        
        if validate:
            result = self.validator.validate_full(email, check_dns=False)
            if not result['syntax_valid']:
                return False, f"Invalid email syntax: {email}"
            if result['is_disposable']:
                return False, f"Disposable email blocked: {email}"
        
        emails = self.load_emails()
        
        if email in emails:
            return False, f"Email already exists: {email}"
        
        emails.append(email)
        self.save_emails(emails)
        return True, f"Added: {email}"
    
    def remove_email(self, email: str) -> Tuple[bool, str]:
        """Remove an email from the list."""
        email = email.strip()
        emails = self.load_emails()
        
        if email not in emails:
            return False, f"Email not found: {email}"
        
        emails.remove(email)
        self.save_emails(emails)
        return True, f"Removed: {email}"
    
    def deduplicate(self) -> int:
        """Remove duplicate emails. Returns count of duplicates removed."""
        emails = self.load_emails()
        original_count = len(emails)
        
        # Remove duplicates while preserving order
        seen = set()
        unique = []
        for email in emails:
            if email.lower() not in seen:
                seen.add(email.lower())
                unique.append(email)
        
        self.save_emails(unique)
        return original_count - len(unique)
    
    def remove_invalid(self, check_dns: bool = False) -> dict:
        """
        Remove invalid emails from the list.
        
        Returns dict with statistics.
        """
        emails = self.load_emails()
        valid = []
        invalid = []
        risky = []
        
        for email in emails:
            result = self.validator.validate_full(email, check_dns=check_dns)
            
            if result['valid'] and result['risk_score'] < 40:
                valid.append(email)
            elif result['risk_score'] >= 40:
                risky.append({'email': email, 'score': result['risk_score']})
            else:
                invalid.append({'email': email, 'reason': result['message']})
        
        self.save_emails(valid)
        
        return {
            'original_count': len(emails),
            'valid': len(valid),
            'removed_invalid': len(invalid),
            'removed_risky': len(risky),
            'invalid_details': invalid,
            'risky_details': risky
        }
    
    def import_csv(self, csv_file: Path, email_column: str = 'email') -> int:
        """
        Import emails from a CSV file.
        
        Args:
            csv_file: Path to CSV file
            email_column: Name of the column containing emails
            
        Returns:
            Number of emails imported
        """
        if not csv_file.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_file}")
        
        imported = 0
        emails = self.load_emails()
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            if email_column not in reader.fieldnames:
                raise ValueError(f"Column '{email_column}' not found in CSV")
            
            for row in reader:
                email = row[email_column].strip()
                if email and email not in emails:
                    result = self.validator.validate_full(email, check_dns=False)
                    if result['syntax_valid'] and not result['is_disposable']:
                        emails.append(email)
                        imported += 1
        
        self.save_emails(emails)
        return imported
    
    def export_csv(self, output_file: Path, include_validation: bool = False):
        """
        Export emails to a CSV file.
        
        Args:
            output_file: Path for output CSV
            include_validation: Whether to include validation columns
        """
        emails = self.load_emails()
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            if include_validation:
                writer = csv.writer(f)
                writer.writerow(['email', 'valid', 'risk_score', 'is_disposable', 'is_role_based'])
                
                for email in emails:
                    result = self.validator.validate_full(email, check_dns=False)
                    writer.writerow([
                        email,
                        result['valid'],
                        result['risk_score'],
                        result['is_disposable'],
                        result['is_role_based']
                    ])
            else:
                writer = csv.writer(f)
                writer.writerow(['email'])
                for email in emails:
                    writer.writerow([email])
    
    def get_statistics(self) -> dict:
        """Get statistics about the email list."""
        emails = self.load_emails()
        
        stats = {
            'total': len(emails),
            'valid': 0,
            'invalid': 0,
            'risky': 0,
            'disposable': 0,
            'role_based': 0,
            'domains': {}
        }
        
        for email in emails:
            result = self.validator.validate_full(email, check_dns=False)
            
            if result['valid'] and result['risk_score'] < 40:
                stats['valid'] += 1
            elif result['risk_score'] >= 40:
                stats['risky'] += 1
            else:
                stats['invalid'] += 1
            
            if result['is_disposable']:
                stats['disposable'] += 1
            if result['is_role_based']:
                stats['role_based'] += 1
            
            # Count domains
            try:
                domain = email.split('@')[1].lower()
                stats['domains'][domain] = stats['domains'].get(domain, 0) + 1
            except IndexError:
                pass
        
        return stats
    
    def search(self, query: str) -> List[str]:
        """Search for emails containing the query string."""
        emails = self.load_emails()
        query = query.lower()
        return [e for e in emails if query in e.lower()]
    
    def clear(self):
        """Clear all emails from the list."""
        self.save_emails([])


if __name__ == '__main__':
    import sys
    
    list_file = Path(__file__).parent / 'data' / 'email_list.txt'
    manager = EmailListManager(list_file)
    
    if len(sys.argv) < 2:
        print("Email List Manager")
        print("=" * 40)
        print("Usage: python email_list_manager.py <command> [args]")
        print("")
        print("Commands:")
        print("  stats              - Show list statistics")
        print("  add <email>        - Add an email")
        print("  remove <email>     - Remove an email")
        print("  dedup              - Remove duplicates")
        print("  clean              - Remove invalid emails")
        print("  search <query>     - Search emails")
        print("  import <file>      - Import from CSV")
        print("  export <file>      - Export to CSV")
        print("  list               - Show all emails")
        sys.exit(0)
    
    command = sys.argv[1]
    
    if command == 'stats':
        stats = manager.get_statistics()
        print(f"\n{'='*50}")
        print("Email List Statistics")
        print(f"{'='*50}")
        print(f"Total emails: {stats['total']}")
        print(f"Valid: {stats['valid']}")
        print(f"Invalid: {stats['invalid']}")
        print(f"Risky: {stats['risky']}")
        print(f"Disposable: {stats['disposable']}")
        print(f"Role-based: {stats['role_based']}")
        print(f"\nTop domains:")
        for domain, count in sorted(stats['domains'].items(), key=lambda x: -x[1])[:10]:
            print(f"  {domain}: {count}")
        print(f"{'='*50}\n")
    
    elif command == 'add' and len(sys.argv) > 2:
        success, msg = manager.add_email(sys.argv[2])
        print(f"{'✓' if success else '✗'} {msg}")
    
    elif command == 'remove' and len(sys.argv) > 2:
        success, msg = manager.remove_email(sys.argv[2])
        print(f"{'✓' if success else '✗'} {msg}")
    
    elif command == 'dedup':
        removed = manager.deduplicate()
        print(f"Removed {removed} duplicate(s)")
    
    elif command == 'clean':
        result = manager.remove_invalid()
        print(f"\nCleaning complete!")
        print(f"  Original: {result['original_count']}")
        print(f"  Valid: {result['valid']}")
        print(f"  Removed (invalid): {result['removed_invalid']}")
        print(f"  Removed (risky): {result['removed_risky']}")
    
    elif command == 'search' and len(sys.argv) > 2:
        results = manager.search(sys.argv[2])
        print(f"Found {len(results)} matching email(s):")
        for email in results[:20]:
            print(f"  {email}")
        if len(results) > 20:
            print(f"  ... and {len(results) - 20} more")
    
    elif command == 'import' and len(sys.argv) > 2:
        try:
            count = manager.import_csv(Path(sys.argv[2]))
            print(f"Imported {count} email(s)")
        except Exception as e:
            print(f"Error: {e}")
    
    elif command == 'export' and len(sys.argv) > 2:
        manager.export_csv(Path(sys.argv[2]), include_validation=True)
        print(f"Exported to {sys.argv[2]}")
    
    elif command == 'list':
        emails = manager.load_emails()
        print(f"\nEmail List ({len(emails)} emails):")
        print("-" * 40)
        for i, email in enumerate(emails[:50], 1):
            print(f"  {i}. {email}")
        if len(emails) > 50:
            print(f"  ... and {len(emails) - 50} more")
        print()
    
    else:
        print(f"Unknown command: {command}")
        print("Run without arguments to see usage")
