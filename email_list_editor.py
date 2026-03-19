"""Email List Quick Editor - Add/delete emails interactively."""
import sys
from pathlib import Path
from datetime import datetime


class EmailListEditor:
    """Quick editor for email list management."""

    def __init__(self, list_file: Path = None):
        self.list_file = list_file or Path(__file__).parent / 'data' / 'email_list.txt'
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Create email list file if it doesn't exist."""
        self.list_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.list_file.exists():
            with open(self.list_file, 'w', encoding='utf-8') as f:
                f.write("# Email List\n# Add emails here (one per line)\n")

    def load_emails(self) -> list:
        """Load all emails from list."""
        if not self.list_file.exists():
            return []
        
        emails = []
        with open(self.list_file, 'r', encoding='utf-8') as f:
            for line in f:
                email = line.strip()
                if email and not email.startswith('#') and '@' in email:
                    emails.append(email.lower())
        return emails

    def save_emails(self, emails: list):
        """Save emails to list file."""
        with open(self.list_file, 'w', encoding='utf-8') as f:
            f.write(f"# Email List - Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# Total emails: {len(emails)}\n\n")
            for email in emails:
                f.write(f"{email}\n")

    def add_emails(self, email_text: str) -> tuple:
        """
        Add multiple emails from pasted text.
        
        Args:
            email_text: Text containing emails (one per line or comma-separated)
        
        Returns:
            Tuple of (added_count, duplicates, invalid)
        """
        existing = self.load_emails()
        added = []
        duplicates = []
        invalid = []

        # Split by newlines or commas
        lines = email_text.replace(',', '\n').split('\n')
        
        for line in lines:
            email = line.strip()
            
            # Skip empty lines and comments
            if not email or email.startswith('#'):
                continue
            
            # Basic email validation
            if '@' not in email or '.' not in email.split('@')[-1]:
                invalid.append(email)
                continue
            
            email = email.lower()
            
            # Check for duplicates
            if email in existing:
                duplicates.append(email)
                continue
            
            added.append(email)
            existing.append(email)

        # Save updated list
        self.save_emails(existing)
        
        return len(added), duplicates, invalid

    def delete_by_number(self, numbers: list) -> tuple:
        """
        Delete emails by their line number.
        
        Args:
            numbers: List of line numbers to delete (1-indexed)
        
        Returns:
            Tuple of (deleted_count, not_found)
        """
        emails = self.load_emails()
        deleted = []
        not_found = []

        # Sort numbers in reverse order to delete from end first
        sorted_numbers = sorted(set(numbers), reverse=True)

        for num in sorted_numbers:
            if num < 1 or num > len(emails):
                not_found.append(num)
            else:
                deleted_email = emails.pop(num - 1)
                deleted.append(deleted_email)

        # Save updated list
        self.save_emails(emails)
        
        return len(deleted), not_found, deleted

    def delete_by_email(self, email: str) -> bool:
        """Delete email by email address."""
        emails = self.load_emails()
        email = email.lower().strip()
        
        if email in emails:
            emails.remove(email)
            self.save_emails(emails)
            return True
        return False

    def list_emails(self, limit: int = None) -> list:
        """List emails with line numbers."""
        emails = self.load_emails()
        
        if limit:
            emails = emails[:limit]
        
        return [(i + 1, email) for i, email in enumerate(emails)]

    def get_statistics(self) -> dict:
        """Get email list statistics."""
        emails = self.load_emails()
        
        # Count by domain
        domains = {}
        for email in emails:
            try:
                domain = email.split('@')[1]
                domains[domain] = domains.get(domain, 0) + 1
            except:
                pass
        
        return {
            'total': len(emails),
            'domains': dict(sorted(domains.items(), key=lambda x: -x[1])[:10])
        }


def print_list(emails: list, show_all: bool = False):
    """Print email list with numbers."""
    if not emails:
        print("\n📭 Email list is empty")
        return
    
    print(f"\n📧 Email List ({len(emails)} emails)")
    print("=" * 60)
    
    limit = 50 if not show_all else len(emails)
    
    for i, email in emails[:limit]:
        print(f"  {i:3d}. {email}")
    
    if len(emails) > limit:
        print(f"\n  ... and {len(emails) - limit} more")
        print(f"  Use 'list all' to see all emails")
    
    print("=" * 60)


def main():
    editor = EmailListEditor()

    print("=" * 60)
    print("📧 Email List Quick Editor")
    print("=" * 60)

    if len(sys.argv) < 2:
        print("\nUsage: python email_list_editor.py <command> [args]")
        print("\nCommands:")
        print("  list [all]              - List emails (first 50 or all)")
        print("  add                     - Add emails (paste text)")
        print("  delete <numbers>        - Delete by line numbers (e.g., 5 or 1,3,7)")
        print("  delete-email <email>    - Delete by email address")
        print("  stats                   - Show statistics")
        print("  search <query>          - Search emails")
        print("\nExamples:")
        print("  python email_list_editor.py list")
        print("  python email_list_editor.py add")
        print("  python email_list_editor.py delete 5")
        print("  python email_list_editor.py delete 1,3,7")
        print("  python email_list_editor.py delete-email user@example.com")
        sys.exit(0)

    command = sys.argv[1]

    if command == 'list':
        show_all = len(sys.argv) > 2 and sys.argv[2] == 'all'
        emails = editor.list_emails()
        print_list(emails, show_all)

    elif command == 'add':
        print("\n📝 Paste emails below (one per line or comma-separated)")
        print("Type 'DONE' on a new line when finished:\n")
        
        lines = []
        while True:
            try:
                line = input()
                if line.strip().upper() == 'DONE':
                    break
                lines.append(line)
            except EOFError:
                break
        
        email_text = '\n'.join(lines)
        added, duplicates, invalid = editor.add_emails(email_text)
        
        print("\n" + "=" * 60)
        print(f"✅ Added: {added} emails")
        if duplicates:
            print(f"⚠️  Duplicates skipped: {len(duplicates)}")
        if invalid:
            print(f"❌ Invalid emails: {len(invalid)}")
            for email in invalid[:5]:
                print(f"    - {email}")
            if len(invalid) > 5:
                print(f"    ... and {len(invalid) - 5} more")
        print("=" * 60)

    elif command == 'delete':
        if len(sys.argv) < 3:
            print("\n❌ Usage: python email_list_editor.py delete <numbers>")
            print("Example: python email_list_editor.py delete 5")
            print("Example: python email_list_editor.py delete 1,3,7")
            sys.exit(1)
        
        # Parse numbers (support comma-separated)
        try:
            numbers = [int(n.strip()) for n in sys.argv[2].split(',')]
        except ValueError:
            print("\n❌ Invalid numbers. Use format: 5 or 1,3,7")
            sys.exit(1)
        
        # Show what will be deleted
        emails = editor.list_emails()
        to_delete = []
        for num in numbers:
            if 1 <= num <= len(emails):
                to_delete.append(emails[num - 1])
        
        print(f"\n⚠️  About to delete {len(to_delete)} email(s):")
        for i, (num, email) in enumerate(to_delete, 1):
            print(f"  {i}. {email} (line {numbers[i-1]})")
        
        confirm = input("\nConfirm? (y/N): ").strip().lower()
        if confirm != 'y':
            print("Cancelled")
            sys.exit(0)
        
        deleted, not_found, deleted_emails = editor.delete_by_number(numbers)
        
        print("\n" + "=" * 60)
        print(f"✅ Deleted: {deleted} emails")
        if not_found:
            print(f"⚠️  Not found: {len(not_found)} (lines: {not_found})")
        print("=" * 60)

    elif command == 'delete-email':
        if len(sys.argv) < 3:
            print("\n❌ Usage: python email_list_editor.py delete-email <email>")
            sys.exit(1)
        
        email = sys.argv[2]
        
        # Find email in list
        emails = editor.load_emails()
        if email.lower() in emails:
            line_num = emails.index(email.lower()) + 1
            print(f"\n⚠️  About to delete: {email} (line {line_num})")
            confirm = input("Confirm? (y/N): ").strip().lower()
            if confirm != 'y':
                print("Cancelled")
                sys.exit(0)
            
            if editor.delete_by_email(email):
                print(f"\n✅ Deleted: {email}")
            else:
                print(f"\n❌ Failed to delete: {email}")
        else:
            print(f"\n❌ Email not found: {email}")

    elif command == 'stats':
        stats = editor.get_statistics()
        print(f"\n📊 Email List Statistics")
        print("=" * 60)
        print(f"Total emails: {stats['total']}")
        print(f"\nTop domains:")
        for domain, count in stats['domains'].items():
            print(f"  {domain}: {count}")
        print("=" * 60)

    elif command == 'search':
        if len(sys.argv) < 3:
            print("\n❌ Usage: python email_list_editor.py search <query>")
            sys.exit(1)
        
        query = sys.argv[2].lower()
        emails = editor.load_emails()
        results = [email for email in emails if query in email]
        
        print(f"\n🔍 Search results for '{query}': {len(results)} found")
        print("=" * 60)
        for i, email in enumerate(results[:50], 1):
            print(f"  {i}. {email}")
        if len(results) > 50:
            print(f"  ... and {len(results) - 50} more")
        print("=" * 60)

    else:
        print(f"\n❌ Unknown command: {command}")
        print("Run without arguments to see usage")


if __name__ == '__main__':
    main()
