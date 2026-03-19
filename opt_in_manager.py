"""Double Opt-In Manager - Manage subscriber consent and confirmation."""
import json
import secrets
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta


class OptInManager:
    """Manage double opt-in subscriptions with consent tracking."""

    def __init__(self, data_file: Path = None):
        self.data_file = data_file or Path(__file__).parent / 'data' / 'opt_in_subscribers.json'
        self.pending_file = Path(__file__).parent / 'data' / 'opt_in_pending.json'
        self._ensure_files_exist()

    def _ensure_files_exist(self):
        """Create data files if they don't exist."""
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        
        if not self.data_file.exists():
            self._save_data([], self.data_file)
        if not self.pending_file.exists():
            self._save_data([], self.pending_file)

    def _load_data(self, file: Path) -> List[Dict]:
        """Load data from JSON file."""
        try:
            with open(file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _save_data(self, data: List[Dict], file: Path):
        """Save data to JSON file."""
        with open(file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)

    def generate_token(self, email: str) -> str:
        """Generate a secure confirmation token."""
        timestamp = datetime.now().isoformat()
        random = secrets.token_hex(16)
        data = f"{email}:{timestamp}:{random}"
        return hashlib.sha256(data.encode()).hexdigest()

    def subscribe(self, email: str, metadata: Dict = None) -> Tuple[bool, str, Optional[str]]:
        """
        Add subscriber to pending list (requires confirmation).
        
        Args:
            email: Subscriber email
            metadata: Optional metadata (ip, source, consent_text, etc.)
        
        Returns:
            Tuple of (success, message, confirmation_token)
        """
        email = email.strip().lower()
        subscribers = self._load_data(self.data_file)
        pending = self._load_data(self.pending_file)

        # Check if already confirmed
        for sub in subscribers:
            if sub['email'] == email:
                return False, f"Already subscribed: {email}", None

        # Check if already pending
        for p in pending:
            if p['email'] == email:
                # Regenerate token if expired
                if datetime.fromisoformat(p['expires_at']) < datetime.now():
                    p['token'] = self.generate_token(email)
                    p['expires_at'] = (datetime.now() + timedelta(days=7)).isoformat()
                    self._save_data(pending, self.pending_file)
                    return True, f"Confirmation email resent to: {email}", p['token']
                return False, f"Confirmation pending for: {email}", None

        # Add to pending
        token = self.generate_token(email)
        pending.append({
            'email': email,
            'token': token,
            'created_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(days=7)).isoformat(),
            'metadata': metadata or {}
        })

        self._save_data(pending, self.pending_file)
        return True, f"Subscription pending - confirmation required", token

    def confirm(self, token: str) -> Tuple[bool, str]:
        """
        Confirm a subscription with token.
        
        Args:
            token: Confirmation token from email
        
        Returns:
            Tuple of (success, message)
        """
        pending = self._load_data(self.pending_file)
        subscribers = self._load_data(self.data_file)

        for i, p in enumerate(pending):
            if p['token'] == token:
                # Check expiration
                if datetime.fromisoformat(p['expires_at']) < datetime.now():
                    pending.pop(i)
                    self._save_data(pending, self.pending_file)
                    return False, "Confirmation token expired - please resubscribe"

                # Move to confirmed subscribers
                subscriber = {
                    'email': p['email'],
                    'confirmed_at': datetime.now().isoformat(),
                    'subscribed_at': p['created_at'],
                    'metadata': p.get('metadata', {}),
                    'status': 'active',
                    'consent_proof': {
                        'ip_address': p.get('metadata', {}).get('ip', 'unknown'),
                        'source': p.get('metadata', {}).get('source', 'unknown'),
                        'timestamp': p['created_at'],
                        'token': token
                    }
                }

                subscribers.append(subscriber)
                pending.pop(i)

                self._save_data(subscribers, self.data_file)
                self._save_data(pending, self.pending_file)
                return True, f"Subscription confirmed for: {p['email']}"

        return False, "Invalid confirmation token"

    def unsubscribe(self, email: str) -> Tuple[bool, str]:
        """Remove subscriber from list."""
        email = email.strip().lower()
        subscribers = self._load_data(self.data_file)
        pending = self._load_data(self.pending_file)

        # Remove from confirmed
        for i, sub in enumerate(subscribers):
            if sub['email'] == email:
                sub['status'] = 'unsubscribed'
                sub['unsubscribed_at'] = datetime.now().isoformat()
                self._save_data(subscribers, self.data_file)
                return True, f"Unsubscribed: {email}"

        # Remove from pending
        for i, p in enumerate(pending):
            if p['email'] == email:
                pending.pop(i)
                self._save_data(pending, self.pending_file)
                return True, f"Removed pending subscription: {email}"

        return False, f"Email not found: {email}"

    def get_subscriber(self, email: str) -> Optional[Dict]:
        """Get subscriber details."""
        email = email.strip().lower()
        subscribers = self._load_data(self.data_file)

        for sub in subscribers:
            if sub['email'] == email:
                return sub
        return None

    def is_subscribed(self, email: str) -> bool:
        """Check if email is confirmed subscriber."""
        sub = self.get_subscriber(email)
        return sub is not None and sub.get('status') == 'active'

    def get_confirmation_link(self, email: str, base_url: str) -> Optional[str]:
        """Generate confirmation link for email."""
        pending = self._load_data(self.pending_file)
        
        for p in pending:
            if p['email'] == email.lower():
                return f"{base_url}/confirm?token={p['token']}"
        return None

    def get_unsubscribe_link(self, email: str, base_url: str) -> str:
        """Generate one-click unsubscribe link."""
        token = hashlib.sha256(f"{email}:unsubscribe".encode()).hexdigest()
        return f"{base_url}/unsubscribe?email={email}&token={token}"

    def cleanup_expired(self) -> int:
        """Remove expired pending subscriptions. Returns count removed."""
        pending = self._load_data(self.pending_file)
        now = datetime.now()
        
        original_count = len(pending)
        pending = [p for p in pending if datetime.fromisoformat(p['expires_at']) > now]
        
        self._save_data(pending, self.pending_file)
        return original_count - len(pending)

    def get_statistics(self) -> Dict:
        """Get opt-in statistics."""
        subscribers = self._load_data(self.data_file)
        pending = self._load_data(self.pending_file)

        active = sum(1 for s in subscribers if s.get('status') == 'active')
        unsubscribed = sum(1 for s in subscribers if s.get('status') == 'unsubscribed')

        # Sources
        sources = {}
        for sub in subscribers:
            source = sub.get('metadata', {}).get('source', 'unknown')
            sources[source] = sources.get(source, 0) + 1

        return {
            'total_subscribers': len(subscribers),
            'active': active,
            'unsubscribed': unsubscribed,
            'pending_confirmation': len(pending),
            'sources': sources,
            'recent_signups_7d': sum(
                1 for s in subscribers 
                if datetime.fromisoformat(s['subscribed_at']) > datetime.now() - timedelta(days=7)
            )
        }

    def export_consent_records(self, output_file: Path):
        """Export consent records for GDPR compliance."""
        subscribers = self._load_data(self.data_file)
        
        records = []
        for sub in subscribers:
            records.append({
                'email': sub['email'],
                'status': sub.get('status', 'unknown'),
                'consent_timestamp': sub.get('subscribed_at', 'unknown'),
                'confirmation_timestamp': sub.get('confirmed_at', 'unknown'),
                'consent_proof': sub.get('consent_proof', {}),
                'unsubscribed_at': sub.get('unsubscribed_at', None)
            })

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(records, f, indent=2, default=str)

    def list_subscribers(self, status: str = 'active') -> List[str]:
        """Get list of subscriber emails by status."""
        subscribers = self._load_data(self.data_file)
        return [s['email'] for s in subscribers if s.get('status') == status]


if __name__ == '__main__':
    import sys

    manager = OptInManager()

    print("=" * 60)
    print("Double Opt-In Manager")
    print("=" * 60)

    if len(sys.argv) < 2:
        print("\nUsage: python opt_in_manager.py <command> [args]")
        print("\nCommands:")
        print("  subscribe <email>           - Add subscriber (pending confirmation)")
        print("  confirm <token>             - Confirm subscription")
        print("  unsubscribe <email>         - Unsubscribe")
        print("  check <email>               - Check subscription status")
        print("  stats                       - Show statistics")
        print("  cleanup                     - Remove expired pending")
        print("  list                        - List all subscribers")
        print("  export <file>               - Export consent records")
        sys.exit(0)

    command = sys.argv[1]

    if command == 'subscribe' and len(sys.argv) > 2:
        email = sys.argv[2]
        metadata = {
            'source': 'cli',
            'ip': '127.0.0.1',
            'consent_text': 'I agree to receive emails'
        }
        success, msg, token = manager.subscribe(email, metadata)
        print(f"{'✓' if success else '✗'} {msg}")
        if token:
            print(f"\nConfirmation token: {token}")
            print(f"Confirmation link: http://localhost:8080/confirm?token={token}")

    elif command == 'confirm' and len(sys.argv) > 2:
        success, msg = manager.confirm(sys.argv[2])
        print(f"{'✓' if success else '✗'} {msg}")

    elif command == 'unsubscribe' and len(sys.argv) > 2:
        success, msg = manager.unsubscribe(sys.argv[2])
        print(f"{'✓' if success else '✗'} {msg}")

    elif command == 'check' and len(sys.argv) > 2:
        sub = manager.get_subscriber(sys.argv[2])
        if sub:
            print(f"\nSubscriber: {sub['email']}")
            print(f"Status: {sub.get('status', 'unknown')}")
            print(f"Subscribed: {sub.get('subscribed_at', 'unknown')}")
            print(f"Confirmed: {sub.get('confirmed_at', 'unknown')}")
            if sub.get('consent_proof'):
                print(f"Consent IP: {sub['consent_proof'].get('ip_address', 'unknown')}")
                print(f"Source: {sub['consent_proof'].get('source', 'unknown')}")
        else:
            print("Not subscribed")

    elif command == 'stats':
        stats = manager.get_statistics()
        print(f"\n{'='*50}")
        print("Opt-In Statistics")
        print(f"{'='*50}")
        print(f"Total subscribers: {stats['total_subscribers']}")
        print(f"Active: {stats['active']}")
        print(f"Unsubscribed: {stats['unsubscribed']}")
        print(f"Pending confirmation: {stats['pending_confirmation']}")
        print(f"Signups (last 7 days): {stats['recent_signups_7d']}")
        print(f"\nSources:")
        for source, count in stats['sources'].items():
            print(f"  {source}: {count}")
        print(f"{'='*50}\n")

    elif command == 'cleanup':
        removed = manager.cleanup_expired()
        print(f"Removed {removed} expired pending subscription(s)")

    elif command == 'list':
        emails = manager.list_subscribers()
        print(f"\nActive Subscribers ({len(emails)}):")
        print("-" * 40)
        for email in emails[:50]:
            print(f"  {email}")
        if len(emails) > 50:
            print(f"  ... and {len(emails) - 50} more")
        print()

    elif command == 'export' and len(sys.argv) > 2:
        manager.export_consent_records(Path(sys.argv[2]))
        print(f"Exported consent records to {sys.argv[2]}")

    else:
        print(f"Unknown command: {command}")
