"""Multiple SMTP Accounts - Rotate between multiple email accounts for bulk sending."""
import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict
from dataclasses import dataclass
from enum import Enum


class AccountStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    RATE_LIMITED = "rate_limited"
    EXHAUSTED = "exhausted"  # Daily limit reached


@dataclass
class SMTPAccount:
    """SMTP Account configuration."""
    id: int
    name: str
    email: str
    password: str
    smtp_server: str
    smtp_port: int
    sender_name: str
    daily_limit: int = 500
    status: str = "active"
    sent_today: int = 0
    last_used: str = None
    created_at: str = None

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'password': self.password,  # Warning: contains password
            'smtp_server': self.smtp_server,
            'smtp_port': self.smtp_port,
            'sender_name': self.sender_name,
            'daily_limit': self.daily_limit,
            'status': self.status,
            'sent_today': self.sent_today,
            'last_used': self.last_used,
            'created_at': self.created_at
        }

    def to_safe_dict(self) -> dict:
        """Return dict without sensitive data."""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'smtp_server': self.smtp_server,
            'smtp_port': self.smtp_port,
            'sender_name': self.sender_name,
            'daily_limit': self.daily_limit,
            'status': self.status,
            'sent_today': self.sent_today,
            'last_used': self.last_used
        }


class SMTPAccountManager:
    """Manage multiple SMTP accounts with rotation and load balancing."""

    def __init__(self, db_path: Path = None):
        if db_path is None:
            db_path = Path(__file__).parent / 'data' / 'smtp_accounts.db'
        
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        self._current_index = 0

    def _init_db(self):
        """Initialize the accounts database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # SMTP accounts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS smtp_accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                smtp_server TEXT NOT NULL,
                smtp_port INTEGER DEFAULT 587,
                sender_name TEXT,
                daily_limit INTEGER DEFAULT 500,
                status TEXT DEFAULT 'active',
                sent_today INTEGER DEFAULT 0,
                last_used TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT
            )
        ''')

        # Daily sending log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER,
                date DATE NOT NULL,
                emails_sent INTEGER DEFAULT 0,
                emails_failed INTEGER DEFAULT 0,
                last_reset TIMESTAMP,
                FOREIGN KEY (account_id) REFERENCES smtp_accounts(id)
            )
        ''')

        # Account usage history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usage_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                action TEXT,
                emails_sent INTEGER DEFAULT 0,
                result TEXT,
                FOREIGN KEY (account_id) REFERENCES smtp_accounts(id)
            )
        ''')

        conn.commit()
        conn.close()

    def add_account(
        self,
        name: str,
        email: str,
        password: str,
        smtp_server: str,
        smtp_port: int = 587,
        sender_name: str = None,
        daily_limit: int = 500,
        notes: str = None
    ) -> int:
        """
        Add a new SMTP account.

        Returns:
            Account ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO smtp_accounts (
                    name, email, password, smtp_server, smtp_port,
                    sender_name, daily_limit, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, email, password, smtp_server, smtp_port, 
                  sender_name or email.split('@')[0], daily_limit, notes))

            account_id = cursor.lastrowid
            conn.commit()
            return account_id

        except sqlite3.IntegrityError:
            raise ValueError(f"Email already registered: {email}")
        finally:
            conn.close()

    def get_account(self, account_id: int) -> Optional[SMTPAccount]:
        """Get account by ID."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM smtp_accounts WHERE id = ?', (account_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return SMTPAccount(**dict(row))
        return None

    def get_account_by_email(self, email: str) -> Optional[SMTPAccount]:
        """Get account by email address."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM smtp_accounts WHERE email = ?', (email,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return SMTPAccount(**dict(row))
        return None

    def get_all_accounts(self, include_inactive: bool = False) -> List[SMTPAccount]:
        """Get all accounts."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if include_inactive:
            cursor.execute('SELECT * FROM smtp_accounts ORDER BY id')
        else:
            cursor.execute("SELECT * FROM smtp_accounts WHERE status != 'inactive' ORDER BY id")

        accounts = [SMTPAccount(**dict(row)) for row in cursor.fetchall()]
        conn.close()

        return accounts

    def update_account(
        self,
        account_id: int,
        name: str = None,
        password: str = None,
        smtp_server: str = None,
        smtp_port: int = None,
        sender_name: str = None,
        daily_limit: int = None,
        status: str = None,
        notes: str = None
    ) -> bool:
        """Update account settings."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        updates = []
        params = []

        if name:
            updates.append('name = ?')
            params.append(name)
        if password:
            updates.append('password = ?')
            params.append(password)
        if smtp_server:
            updates.append('smtp_server = ?')
            params.append(smtp_server)
        if smtp_port:
            updates.append('smtp_port = ?')
            params.append(smtp_port)
        if sender_name:
            updates.append('sender_name = ?')
            params.append(sender_name)
        if daily_limit:
            updates.append('daily_limit = ?')
            params.append(daily_limit)
        if status:
            updates.append('status = ?')
            params.append(status)
        if notes:
            updates.append('notes = ?')
            params.append(notes)

        if not updates:
            conn.close()
            return False

        params.append(account_id)
        cursor.execute(f'''
            UPDATE smtp_accounts 
            SET {', '.join(updates)}
            WHERE id = ?
        ''', params)

        conn.commit()
        conn.close()

        return True

    def delete_account(self, account_id: int) -> bool:
        """Delete an account."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('DELETE FROM smtp_accounts WHERE id = ?', (account_id,))
        cursor.execute('DELETE FROM daily_log WHERE account_id = ?', (account_id,))
        cursor.execute('DELETE FROM usage_history WHERE account_id = ?', (account_id,))

        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()

        return deleted

    def get_next_account(self) -> Optional[SMTPAccount]:
        """
        Get the next available account using round-robin rotation.
        
        Skips accounts that are:
        - Inactive
        - Rate limited
        - At daily limit
        """
        accounts = self.get_all_accounts()
        
        if not accounts:
            return None

        # Find available accounts
        available = [a for a in accounts if a.status == AccountStatus.ACTIVE.value 
                     and a.sent_today < a.daily_limit]

        if not available:
            return None

        # Round-robin selection
        account = available[self._current_index % len(available)]
        self._current_index += 1

        return account

    def get_best_account(self) -> Optional[SMTPAccount]:
        """
        Get the best account based on remaining daily capacity.
        
        Returns the account with the most remaining sends.
        """
        accounts = self.get_all_accounts()
        
        if not accounts:
            return None

        # Filter available accounts
        available = [
            a for a in accounts 
            if a.status == AccountStatus.ACTIVE.value and a.sent_today < a.daily_limit
        ]

        if not available:
            return None

        # Return account with most remaining capacity
        return max(available, key=lambda a: a.daily_limit - a.sent_today)

    def record_send(self, account_id: int, success: bool = True):
        """Record an email send for an account."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        today = datetime.now().date().isoformat()

        # Update sent count
        cursor.execute('''
            UPDATE smtp_accounts 
            SET sent_today = sent_today + 1, last_used = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (account_id,))

        # Update or create daily log
        cursor.execute('''
            INSERT INTO daily_log (account_id, date, emails_sent, emails_failed)
            VALUES (?, ?, 1, 0)
            ON CONFLICT(account_id, date) DO UPDATE SET
                emails_sent = emails_sent + CASE WHEN ? THEN 1 ELSE 0 END,
                emails_failed = emails_failed + CASE WHEN ? THEN 1 ELSE 0 END
        ''', (account_id, today, success, not success))

        # Log to history
        cursor.execute('''
            INSERT INTO usage_history (account_id, action, emails_sent, result)
            VALUES (?, 'send', 1, ?)
        ''', (account_id, 'success' if success else 'failed'))

        # Check if daily limit reached
        cursor.execute('SELECT sent_today, daily_limit FROM smtp_accounts WHERE id = ?', (account_id,))
        row = cursor.fetchone()
        if row and row[0] >= row[1]:
            cursor.execute('''
                UPDATE smtp_accounts SET status = ? WHERE id = ?
            ''', (AccountStatus.EXHAUSTED.value, account_id))

        conn.commit()
        conn.close()

    def reset_daily_counts(self):
        """Reset daily send counts for all accounts."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        today = datetime.now().date().isoformat()

        # Reset all accounts
        cursor.execute('''
            UPDATE smtp_accounts 
            SET sent_today = 0, status = 'active'
            WHERE status = 'exhausted'
        ''')

        # Create new daily log entries
        accounts = self.get_all_accounts(include_inactive=True)
        for account in accounts:
            cursor.execute('''
                INSERT OR IGNORE INTO daily_log (account_id, date)
                VALUES (?, ?)
            ''', (account.id, today))

        conn.commit()
        conn.close()

    def set_account_status(self, account_id: int, status: AccountStatus):
        """Set account status."""
        self.update_account(account_id, status=status.value)
        
        if status == AccountStatus.RATE_LIMITED:
            self._log_action(account_id, 'rate_limited', 'Account temporarily rate limited')

    def _log_action(self, account_id: int, action: str, result: str):
        """Log an account action."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO usage_history (account_id, action, result)
            VALUES (?, ?, ?)
        ''', (account_id, action, result))

        conn.commit()
        conn.close()

    def get_usage_stats(self, account_id: int = None, days: int = 7) -> dict:
        """Get usage statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        stats = {}

        if account_id:
            # Stats for specific account
            cursor.execute('''
                SELECT 
                    SUM(emails_sent) as total_sent,
                    SUM(emails_failed) as total_failed
                FROM daily_log 
                WHERE account_id = ? AND date >= date('now', ?)
            ''', (account_id, f'-{days} days'))
            row = cursor.fetchone()
            stats = {
                'account_id': account_id,
                'total_sent': row[0] or 0,
                'total_failed': row[1] or 0,
                'period_days': days
            }
        else:
            # Overall stats
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_accounts,
                    SUM(sent_today) as sent_today,
                    SUM(daily_limit) as total_capacity
                FROM smtp_accounts
                WHERE status != 'inactive'
            ''')
            row = cursor.fetchone()
            stats = {
                'total_accounts': row[0] or 0,
                'sent_today': row[1] or 0,
                'total_capacity': row[2] or 0,
                'remaining_capacity': (row[2] or 0) - (row[1] or 0)
            }

            # By status
            cursor.execute('''
                SELECT status, COUNT(*) as count 
                FROM smtp_accounts 
                GROUP BY status
            ''')
            stats['by_status'] = {row[0]: row[1] for row in cursor.fetchall()}

        conn.close()
        return stats

    def get_accounts_summary(self) -> List[dict]:
        """Get summary of all accounts."""
        accounts = self.get_all_accounts(include_inactive=True)
        return [account.to_safe_dict() for account in accounts]

    def export_accounts(self, output_file: Path, include_passwords: bool = False) -> Path:
        """Export accounts to JSON file."""
        accounts = self.get_all_accounts(include_inactive=True)
        
        data = {
            'exported_at': datetime.now().isoformat(),
            'accounts': []
        }

        for account in accounts:
            if include_passwords:
                data['accounts'].append(account.to_dict())
            else:
                data['accounts'].append(account.to_safe_dict())

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        return output_file

    def import_accounts(self, input_file: Path) -> int:
        """Import accounts from JSON file."""
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        imported = 0
        for acc_data in data.get('accounts', []):
            try:
                self.add_account(
                    name=acc_data['name'],
                    email=acc_data['email'],
                    password=acc_data['password'],
                    smtp_server=acc_data['smtp_server'],
                    smtp_port=acc_data.get('smtp_port', 587),
                    sender_name=acc_data.get('sender_name'),
                    daily_limit=acc_data.get('daily_limit', 500)
                )
                imported += 1
            except ValueError:
                pass  # Skip duplicates

        return imported


if __name__ == '__main__':
    import sys

    print("=" * 60)
    print("SMTP Account Manager")
    print("=" * 60)

    manager = SMTPAccountManager()

    if len(sys.argv) < 2:
        print("\nUsage: python smtp_account_manager.py <command> [args]")
        print("\nCommands:")
        print("  add <name> <email> <password> <smtp_server> [port] [daily_limit]")
        print("  list                  - List all accounts")
        print("  next                  - Get next available account")
        print("  best                  - Get best account (most capacity)")
        print("  stats                 - Show usage statistics")
        print("  reset                 - Reset daily counts")
        print("  status <id> <status>  - Set account status")
        print("  delete <id>           - Delete an account")
        print("  export <file>         - Export accounts to JSON")
        print("  import <file>         - Import accounts from JSON")
        sys.exit(0)

    command = sys.argv[1]

    if command == 'add' and len(sys.argv) >= 6:
        try:
            account_id = manager.add_account(
                name=sys.argv[2],
                email=sys.argv[3],
                password=sys.argv[4],
                smtp_server=sys.argv[5],
                smtp_port=int(sys.argv[6]) if len(sys.argv) > 6 else 587,
                daily_limit=int(sys.argv[7]) if len(sys.argv) > 7 else 500
            )
            print(f"✓ Account added with ID: {account_id}")
        except ValueError as e:
            print(f"✗ Error: {e}")

    elif command == 'list':
        accounts = manager.get_accounts_summary()
        if not accounts:
            print("\nNo accounts configured")
        else:
            print(f"\n{'ID':<4} {'Name':<15} {'Email':<25} {'Status':<12} {'Sent':<8} {'Limit':<8}")
            print("-" * 75)
            for acc in accounts:
                print(f"{acc['id']:<4} {acc['name']:<15} {acc['email']:<25} "
                      f"{acc['status']:<12} {acc['sent_today']:<8} {acc['daily_limit']:<8}")

    elif command == 'next':
        account = manager.get_next_account()
        if account:
            print(f"\nNext Account:")
            print(f"  ID: {account.id}")
            print(f"  Name: {account.name}")
            print(f"  Email: {account.email}")
            print(f"  SMTP: {account.smtp_server}:{account.smtp_port}")
            print(f"  Remaining: {account.daily_limit - account.sent_today}/{account.daily_limit}")
        else:
            print("\nNo available accounts")

    elif command == 'best':
        account = manager.get_best_account()
        if account:
            print(f"\nBest Account:")
            print(f"  ID: {account.id}")
            print(f"  Name: {account.name}")
            print(f"  Email: {account.email}")
            print(f"  Remaining: {account.daily_limit - account.sent_today}/{account.daily_limit}")
        else:
            print("\nNo available accounts")

    elif command == 'stats':
        stats = manager.get_usage_stats()
        print(f"\nUsage Statistics:")
        print(f"  Total Accounts: {stats.get('total_accounts', 0)}")
        print(f"  Sent Today: {stats.get('sent_today', 0)}/{stats.get('total_capacity', 0)}")
        print(f"  Remaining: {stats.get('remaining_capacity', 0)}")
        print(f"  By Status: {stats.get('by_status', {})}")

    elif command == 'reset':
        manager.reset_daily_counts()
        print("✓ Daily counts reset")

    elif command == 'status' and len(sys.argv) >= 4:
        account_id = int(sys.argv[2])
        status = sys.argv[3]
        try:
            manager.set_account_status(account_id, AccountStatus(status))
            print(f"✓ Account {account_id} status set to {status}")
        except ValueError:
            print(f"Invalid status. Use: active, inactive, rate_limited, exhausted")

    elif command == 'delete' and len(sys.argv) >= 3:
        account_id = int(sys.argv[2])
        if manager.delete_account(account_id):
            print(f"✓ Account {account_id} deleted")
        else:
            print(f"✗ Account {account_id} not found")

    elif command == 'export' and len(sys.argv) >= 3:
        output_file = Path(sys.argv[2])
        include_pw = '--with-passwords' in sys.argv
        manager.export_accounts(output_file, include_passwords=include_pw)
        print(f"✓ Accounts exported to {output_file}")

    elif command == 'import' and len(sys.argv) >= 3:
        input_file = Path(sys.argv[2])
        count = manager.import_accounts(input_file)
        print(f"✓ Imported {count} accounts")

    else:
        print(f"Unknown command: {command}")
        print("Run without arguments to see usage")
