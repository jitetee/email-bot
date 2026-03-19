"""Bounce Handler - Track and handle bounced emails."""
import re
import sqlite3
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from enum import Enum
from email.message import Message
from email.parser import Parser


class BounceType(Enum):
    HARD = "hard"      # Permanent failure (invalid email, domain doesn't exist)
    SOFT = "soft"      # Temporary failure (mailbox full, server down)
    SPAM = "spam"      # Marked as spam
    UNSUBSCRIBE = "unsubscribe"  # User unsubscribed
    UNKNOWN = "unknown"


class BounceHandler:
    """Track and handle email bounces."""

    # Common bounce patterns
    HARD_BOUNCE_PATTERNS = [
        r'user unknown', r'no such user', r'invalid address', r'address rejected',
        r'mailbox not found', r'unknown user', r'account disabled', r'user not found',
        r'no such mailbox', r'recipient rejected', r'invalid mailbox', r'bad address',
        r'undeliverable', r'permanent failure', r'5\.1\.\d', r'5\.2\.\d', r'5\.5\.\d'
    ]

    SOFT_BOUNCE_PATTERNS = [
        r'mailbox full', r'quota exceeded', r'over quota', r'mailbox over quota',
        r'temporary failure', r'try again later', r'server busy', r'connection timeout',
        r'deferred', r'greylisted', r'rate limited', r'too many connections',
        r'4\.2\.\d', r'4\.3\.\d', r'4\.7\.\d'
    ]

    SPAM_PATTERNS = [
        r'spam', r'junk', r'blocked', r'rejected.*spam', r'marked as spam',
        r'content filter', r'policy rejection'
    ]

    UNSUBSCRIBE_PATTERNS = [
        r'unsubscribe', r'opt.?out', r'remove.*list', r'stop.*mail'
    ]

    def __init__(self, db_path: Path = None):
        if db_path is None:
            db_path = Path(__file__).parent / 'data' / 'bounces.db'
        
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize the bounce tracking database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Bounces table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bounces (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                bounce_type TEXT NOT NULL,
                reason TEXT,
                bounce_message TEXT,
                campaign_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processed INTEGER DEFAULT 0,
                action_taken TEXT,
                original_rcpt TEXT,
                final_rcpt TEXT,
                diagnostic_code TEXT,
                remote_mta TEXT,
                reporting_mta TEXT
            )
        ''')

        # Suppression list (emails that should not receive future emails)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS suppression_list (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                reason TEXT,
                bounce_type TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                campaign_id INTEGER,
                is_permanent INTEGER DEFAULT 0
            )
        ''')

        # Bounce processing log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bounce_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                action TEXT,
                email TEXT,
                details TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def classify_bounce(self, bounce_message: str) -> BounceType:
        """Classify a bounce based on the bounce message."""
        message_lower = bounce_message.lower()

        # Check for unsubscribe
        for pattern in self.UNSUBSCRIBE_PATTERNS:
            if re.search(pattern, message_lower):
                return BounceType.UNSUBSCRIBE

        # Check for spam
        for pattern in self.SPAM_PATTERNS:
            if re.search(pattern, message_lower):
                return BounceType.SPAM

        # Check for hard bounce
        for pattern in self.HARD_BOUNCE_PATTERNS:
            if re.search(pattern, message_lower):
                return BounceType.HARD

        # Check for soft bounce
        for pattern in self.SOFT_BOUNCE_PATTERNS:
            if re.search(pattern, message_lower):
                return BounceType.SOFT

        return BounceType.UNKNOWN

    def record_bounce(
        self,
        email: str,
        bounce_message: str = None,
        campaign_id: int = None,
        bounce_type: BounceType = None
    ) -> int:
        """
        Record a bounce.

        Args:
            email: Bounced email address
            bounce_message: Full bounce notification message
            campaign_id: Related campaign ID
            bounce_type: Pre-determined bounce type (auto-detected if not provided)

        Returns:
            Bounce record ID
        """
        if bounce_type is None and bounce_message:
            bounce_type = self.classify_bounce(bounce_message)
        elif bounce_type is None:
            bounce_type = BounceType.UNKNOWN

        # Parse bounce message for details
        bounce_info = self._parse_bounce_message(bounce_message) if bounce_message else {}

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO bounces (
                email, bounce_type, reason, bounce_message, campaign_id,
                original_rcpt, final_rcpt, diagnostic_code, remote_mta, reporting_mta
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            email, bounce_type.value, bounce_info.get('reason'), bounce_message,
            campaign_id, bounce_info.get('original_rcpt'), bounce_info.get('final_rcpt'),
            bounce_info.get('diagnostic_code'), bounce_info.get('remote_mta'),
            bounce_info.get('reporting_mta')
        ))

        bounce_id = cursor.lastrowid

        # Auto-add to suppression list for hard bounces
        if bounce_type == BounceType.HARD:
            self._add_to_suppression(email, bounce_type, bounce_message, campaign_id, is_permanent=True)
        elif bounce_type == BounceType.SPAM:
            self._add_to_suppression(email, bounce_type, bounce_message, campaign_id, is_permanent=True)
        elif bounce_type == BounceType.UNSUBSCRIBE:
            self._add_to_suppression(email, bounce_type, bounce_message, campaign_id, is_permanent=True)

        self._log_action('bounce_recorded', email, f'Type: {bounce_type.value}, ID: {bounce_id}')

        conn.commit()
        conn.close()

        return bounce_id

    def _parse_bounce_message(self, message: str) -> dict:
        """Parse bounce message for structured information."""
        info = {}

        # Try to extract diagnostic code
        diagnostic_match = re.search(r'Diagnostic-Code:\s*(.+?)(?:\n|$)', message, re.IGNORECASE)
        if diagnostic_match:
            info['diagnostic_code'] = diagnostic_match.group(1).strip()

        # Try to extract original recipient
        orig_match = re.search(r'Original-Recipient:\s*(.+?)(?:\n|$)', message, re.IGNORECASE)
        if orig_match:
            info['original_rcpt'] = orig_match.group(1).strip()

        # Try to extract final recipient
        final_match = re.search(r'Final-Recipient:\s*(.+?)(?:\n|$)', message, re.IGNORECASE)
        if final_match:
            info['final_rcpt'] = final_match.group(1).strip()

        # Try to extract remote MTA
        remote_match = re.search(r'Remote-MTA:\s*(.+?)(?:\n|$)', message, re.IGNORECASE)
        if remote_match:
            info['remote_mta'] = remote_match.group(1).strip()

        # Try to extract reporting MTA
        reporting_match = re.search(r'Reporting-MTA:\s*(.+?)(?:\n|$)', message, re.IGNORECASE)
        if reporting_match:
            info['reporting_mta'] = reporting_match.group(1).strip()

        # Extract reason from common patterns
        reason_patterns = [
            (r'User unknown', 'User unknown'),
            (r'Mailbox full', 'Mailbox full'),
            (r'Quota exceeded', 'Quota exceeded'),
            (r'Invalid address', 'Invalid address'),
            (r'No such user', 'No such user'),
        ]
        for pattern, reason in reason_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                info['reason'] = reason
                break

        return info

    def _add_to_suppression(
        self, 
        email: str, 
        bounce_type: BounceType, 
        reason: str = None,
        campaign_id: int = None,
        is_permanent: bool = False
    ):
        """Add email to suppression list."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        expires_at = None
        if bounce_type == BounceType.SOFT and not is_permanent:
            # Soft bounces expire after 7 days
            expires_at = (datetime.now() + timedelta(days=7)).isoformat()

        try:
            cursor.execute('''
                INSERT OR REPLACE INTO suppression_list 
                (email, reason, bounce_type, expires_at, campaign_id, is_permanent)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (email, reason, bounce_type.value, expires_at, campaign_id, 1 if is_permanent else 0))
        except sqlite3.IntegrityError:
            pass  # Already in suppression list

        conn.commit()
        conn.close()

    def is_suppressed(self, email: str) -> bool:
        """Check if an email is on the suppression list."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check if email is suppressed (and not expired)
        cursor.execute('''
            SELECT COUNT(*) FROM suppression_list 
            WHERE email = ? AND (expires_at IS NULL OR expires_at > datetime('now'))
        ''', (email.lower(),))

        is_suppressed = cursor.fetchone()[0] > 0
        conn.close()

        return is_suppressed

    def get_suppression_list(self, limit: int = 100) -> List[dict]:
        """Get the suppression list."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM suppression_list 
            WHERE expires_at IS NULL OR expires_at > datetime('now')
            ORDER BY added_at DESC
            LIMIT ?
        ''', (limit,))

        results = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return results

    def remove_from_suppression(self, email: str) -> bool:
        """Remove an email from the suppression list."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('DELETE FROM suppression_list WHERE email = ?', (email.lower(),))
        removed = cursor.rowcount > 0

        if removed:
            self._log_action('suppression_removed', email, 'Manually removed from suppression list')

        conn.commit()
        conn.close()

        return removed

    def clean_expired_suppressions(self) -> int:
        """Remove expired entries from suppression list."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            DELETE FROM suppression_list 
            WHERE expires_at IS NOT NULL AND expires_at <= datetime('now')
        ''')

        removed = cursor.rowcount
        conn.commit()
        conn.close()

        if removed > 0:
            self._log_action('cleanup', None, f'Removed {removed} expired suppressions')

        return removed

    def get_bounce_stats(self, campaign_id: int = None) -> dict:
        """Get bounce statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        stats = {}

        if campaign_id:
            # Stats for specific campaign
            cursor.execute('''
                SELECT bounce_type, COUNT(*) as count 
                FROM bounces WHERE campaign_id = ?
                GROUP BY bounce_type
            ''', (campaign_id,))
            stats['by_type'] = {row[0]: row[1] for row in cursor.fetchall()}
            cursor.execute('SELECT COUNT(*) FROM bounces WHERE campaign_id = ?', (campaign_id,))
            stats['total'] = cursor.fetchone()[0]
        else:
            # Overall stats
            cursor.execute('''
                SELECT bounce_type, COUNT(*) as count 
                FROM bounces 
                GROUP BY bounce_type
            ''')
            stats['by_type'] = {row[0]: row[1] for row in cursor.fetchall()}

            cursor.execute('SELECT COUNT(*) FROM bounces')
            stats['total'] = cursor.fetchone()[0]

            # Last 24 hours
            cursor.execute('''
                SELECT COUNT(*) FROM bounces 
                WHERE created_at >= datetime('now', '-1 day')
            ''')
            stats['last_24h'] = cursor.fetchone()[0]

            # Last 7 days
            cursor.execute('''
                SELECT COUNT(*) FROM bounces 
                WHERE created_at >= datetime('now', '-7 days')
            ''')
            stats['last_7d'] = cursor.fetchone()[0]

            # Suppression list size
            cursor.execute('''
                SELECT COUNT(*) FROM suppression_list 
                WHERE expires_at IS NULL OR expires_at > datetime('now')
            ''')
            stats['suppressed'] = cursor.fetchone()[0]

        conn.close()
        return stats

    def get_bounces(self, campaign_id: int = None, limit: int = 50) -> List[dict]:
        """Get recent bounces."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if campaign_id:
            cursor.execute('''
                SELECT * FROM bounces 
                WHERE campaign_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (campaign_id, limit))
        else:
            cursor.execute('''
                SELECT * FROM bounces 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))

        bounces = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return bounces

    def _log_action(self, action: str, email: str = None, details: str = None):
        """Log a bounce handling action."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO bounce_log (action, email, details)
            VALUES (?, ?, ?)
        ''', (action, email, details))

        conn.commit()
        conn.close()

    def process_bounce_email(self, email_content: str, campaign_id: int = None) -> Optional[int]:
        """
        Process a bounce notification email.

        Args:
            email_content: Raw email content of bounce notification
            campaign_id: Related campaign ID

        Returns:
            Bounce record ID if processed successfully
        """
        parser = Parser()
        message = parser.parsestr(email_content)

        # Extract bounced email from message
        bounced_email = self._extract_bounced_email(message)
        if not bounced_email:
            return None

        # Classify and record bounce
        bounce_type = self.classify_bounce(email_content)
        return self.record_bounce(bounced_email, email_content, campaign_id, bounce_type)

    def _extract_bounced_email(self, message: Message) -> Optional[str]:
        """Extract the bounced email address from a bounce message."""
        # Try various headers
        headers_to_check = [
            'X-Failed-Recipients',
            'X-Original-Recipient',
            'Final-Recipient',
            'Original-Recipient'
        ]

        for header in headers_to_check:
            value = message.get(header, '')
            if value:
                # Extract email from header value
                email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', value)
                if email_match:
                    return email_match.group(0)

        # Try to find email in body
        body = self._get_email_body(message)
        email_patterns = [
            r'<([\w\.-]+@[\w\.-]+\.\w+)>',
            r'address:\s*([\w\.-]+@[\w\.-]+\.\w+)',
            r'recipient:\s*([\w\.-]+@[\w\.-]+\.\w+)',
        ]

        for pattern in email_patterns:
            match = re.search(pattern, body, re.IGNORECASE)
            if match:
                return match.group(1)

        return None

    def _get_email_body(self, message: Message) -> str:
        """Extract text body from email message."""
        if message.is_multipart():
            for part in message.walk():
                content_type = part.get_content_type()
                if content_type == 'text/plain':
                    try:
                        return part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    except:
                        pass
        else:
            try:
                return message.get_payload(decode=True).decode('utf-8', errors='ignore')
            except:
                return str(message.get_payload())
        return ""

    def export_suppression_list(self, output_file: Path) -> Path:
        """Export suppression list to file."""
        suppressions = self.get_suppression_list(limit=10000)

        with open(output_file, 'w', encoding='utf-8') as f:
            for suppression in suppressions:
                f.write(f"{suppression['email']}\n")

        return output_file

    def import_suppression_list(self, input_file: Path, reason: str = "Imported") -> int:
        """Import emails to suppression list."""
        if not input_file.exists():
            raise FileNotFoundError(f"File not found: {input_file}")

        imported = 0
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        with open(input_file, 'r', encoding='utf-8') as f:
            for line in f:
                email = line.strip()
                if email and '@' in email:
                    try:
                        cursor.execute('''
                            INSERT OR IGNORE INTO suppression_list 
                            (email, reason, bounce_type, is_permanent)
                            VALUES (?, ?, ?, 1)
                        ''', (email.lower(), reason, 'imported'))
                        imported += 1
                    except:
                        pass

        conn.commit()
        conn.close()

        self._log_action('suppression_import', None, f'Imported {imported} emails from {input_file}')

        return imported


if __name__ == '__main__':
    import sys

    print("=" * 60)
    print("Bounce Handler")
    print("=" * 60)

    handler = BounceHandler()

    if len(sys.argv) < 2:
        print("\nUsage: python bounce_handler.py <command> [args]")
        print("\nCommands:")
        print("  stats                 - Show bounce statistics")
        print("  list [limit]          - List recent bounces")
        print("  suppression [limit]   - Show suppression list")
        print("  check <email>         - Check if email is suppressed")
        print("  remove <email>        - Remove from suppression list")
        print("  clean                 - Remove expired suppressions")
        print("  export <file>         - Export suppression list")
        print("  import <file>         - Import suppression list")
        print("  demo                  - Create demo bounces")
        sys.exit(0)

    command = sys.argv[1]

    if command == 'stats':
        stats = handler.get_bounce_stats()
        print(f"\nBounce Statistics:")
        print(f"  Total Bounces: {stats.get('total', 0)}")
        print(f"  Last 24 Hours: {stats.get('last_24h', 0)}")
        print(f"  Last 7 Days: {stats.get('last_7d', 0)}")
        print(f"  Suppressed: {stats.get('suppressed', 0)}")
        print(f"  By Type: {stats.get('by_type', {})}")

    elif command == 'list':
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 20
        bounces = handler.get_bounces(limit=limit)
        if not bounces:
            print("\nNo bounces recorded")
        else:
            print(f"\n{'ID':<6} {'Email':<30} {'Type':<8} {'Date':<20}")
            print("-" * 70)
            for b in bounces:
                print(f"{b['id']:<6} {b['email']:<30} {b['bounce_type']:<8} {b['created_at'][:16]:<20}")

    elif command == 'suppression':
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 20
        suppressions = handler.get_suppression_list(limit=limit)
        if not suppressions:
            print("\nSuppression list is empty")
        else:
            print(f"\n{'Email':<35} {'Type':<12} {'Permanent':<10} {'Date Added':<20}")
            print("-" * 80)
            for s in suppressions:
                perm = "Yes" if s['is_permanent'] else "No"
                print(f"{s['email']:<35} {s['bounce_type']:<12} {perm:<10} {s['added_at'][:16]:<20}")

    elif command == 'check':
        email = sys.argv[2]
        if handler.is_suppressed(email):
            print(f"\n⚠️  {email} is on the suppression list")
        else:
            print(f"\n✓ {email} is NOT on the suppression list")

    elif command == 'remove':
        email = sys.argv[2]
        if handler.remove_from_suppression(email):
            print(f"✓ Removed {email} from suppression list")
        else:
            print(f"✗ {email} was not on the suppression list")

    elif command == 'clean':
        removed = handler.clean_expired_suppressions()
        print(f"✓ Removed {removed} expired suppressions")

    elif command == 'export' and len(sys.argv) > 2:
        output_file = Path(sys.argv[2])
        handler.export_suppression_list(output_file)
        print(f"✓ Suppression list exported to {output_file}")

    elif command == 'import' and len(sys.argv) > 2:
        input_file = Path(sys.argv[2])
        count = handler.import_suppression_list(input_file)
        print(f"✓ Imported {count} emails to suppression list")

    elif command == 'demo':
        # Create demo bounces
        demo_bounces = [
            ('invalid@example.com', 'User unknown - no such mailbox', BounceType.HARD),
            ('full@example.com', 'Mailbox full, quota exceeded', BounceType.SOFT),
            ('spam@example.com', 'Message marked as spam by content filter', BounceType.SPAM),
            ('unsub@example.com', 'User requested to unsubscribe from list', BounceType.UNSUBSCRIBE),
        ]

        for email, message, bounce_type in demo_bounces:
            handler.record_bounce(email, message, bounce_type=bounce_type)
            print(f"✓ Recorded {bounce_type.value} bounce for {email}")

        print("\nDemo bounces created. Run 'stats' to see summary.")

    else:
        print(f"Unknown command: {command}")
        print("Run without arguments to see usage")
