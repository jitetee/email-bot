"""Engagement Tracker - Track opens, clicks, and subscriber engagement scoring."""
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict


class EngagementTracker:
    """Track and score subscriber engagement for email campaigns."""

    def __init__(self, data_file: Path = None):
        self.data_file = data_file or Path(__file__).parent / 'data' / 'engagement.json'
        self.campaign_file = Path(__file__).parent / 'data' / 'engagement_campaigns.json'
        self._ensure_files_exist()

    def _ensure_files_exist(self):
        """Create data files if they don't exist."""
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        
        if not self.data_file.exists():
            self._save_data({}, self.data_file)
        if not self.campaign_file.exists():
            self._save_data([], self.campaign_file)

    def _load_data(self, file: Path):
        """Load data from JSON file."""
        try:
            with open(file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {} if file == self.data_file else []

    def _save_data(self, data, file: Path):
        """Save data to JSON file."""
        with open(file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)

    def _get_subscriber_data(self, email: str) -> Dict:
        """Get engagement data for a subscriber."""
        data = self._load_data(self.data_file)
        email_lower = email.lower()
        
        if email_lower not in data:
            data[email_lower] = {
                'email': email_lower,
                'total_sent': 0,
                'total_opens': 0,
                'total_clicks': 0,
                'unique_opens': 0,
                'unique_clicks': 0,
                'last_sent': None,
                'last_open': None,
                'last_click': None,
                'first_seen': datetime.now().isoformat(),
                'engagement_score': 0,
                'engagement_level': 'unknown',
                'campaigns': {},
                'click_history': [],
                'open_history': []
            }
        
        return data[email_lower]

    def _save_subscriber_data(self, email: str, subscriber_data: Dict):
        """Save engagement data for a subscriber."""
        data = self._load_data(self.data_file)
        data[email.lower()] = subscriber_data
        self._save_data(data, self.data_file)

    def record_sent(self, email: str, campaign_id: str, campaign_name: str = None):
        """Record that an email was sent to a subscriber."""
        subscriber = self._get_subscriber_data(email)
        
        subscriber['total_sent'] += 1
        subscriber['last_sent'] = datetime.now().isoformat()
        
        # Track per campaign
        if campaign_id not in subscriber['campaigns']:
            subscriber['campaigns'][campaign_id] = {
                'name': campaign_name,
                'sent': datetime.now().isoformat(),
                'opened': False,
                'clicked': False,
                'open_count': 0,
                'click_count': 0
            }
        else:
            subscriber['campaigns'][campaign_id]['sent'] = datetime.now().isoformat()

        self._save_subscriber_data(email, subscriber)

    def record_open(self, email: str, campaign_id: str, ip_address: str = None, 
                   user_agent: str = None) -> bool:
        """
        Record an email open (via tracking pixel).
        
        Returns True if this is a new unique open.
        """
        subscriber = self._get_subscriber_data(email)
        campaign = subscriber['campaigns'].get(campaign_id)
        
        if not campaign:
            return False

        is_unique = not campaign['opened']
        campaign['opened'] = True
        campaign['open_count'] += 1
        
        subscriber['total_opens'] += 1
        if is_unique:
            subscriber['unique_opens'] += 1
            subscriber['last_open'] = datetime.now().isoformat()
        
        # Record open event
        open_event = {
            'campaign_id': campaign_id,
            'timestamp': datetime.now().isoformat(),
            'ip': ip_address,
            'user_agent': user_agent
        }
        subscriber['open_history'].append(open_event)
        
        # Keep only last 100 events
        subscriber['open_history'] = subscriber['open_history'][-100:]

        # Recalculate engagement score
        self._calculate_engagement_score(subscriber)
        
        self._save_subscriber_data(email, subscriber)
        return is_unique

    def record_click(self, email: str, campaign_id: str, url: str,
                    ip_address: str = None, user_agent: str = None) -> bool:
        """
        Record a link click (via tracking redirect).
        
        Returns True if this is a new unique click for this campaign.
        """
        subscriber = self._get_subscriber_data(email)
        campaign = subscriber['campaigns'].get(campaign_id)
        
        if not campaign:
            campaign = {
                'name': 'Unknown',
                'sent': None,
                'opened': False,
                'clicked': True,
                'open_count': 0,
                'click_count': 1
            }
            subscriber['campaigns'][campaign_id] = campaign

        is_unique = not campaign['clicked']
        campaign['clicked'] = True
        campaign['click_count'] += 1
        
        subscriber['total_clicks'] += 1
        if is_unique:
            subscriber['unique_clicks'] += 1
            subscriber['last_click'] = datetime.now().isoformat()
        
        # Record click event
        click_event = {
            'campaign_id': campaign_id,
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'ip': ip_address,
            'user_agent': user_agent
        }
        subscriber['click_history'].append(click_event)
        
        # Keep only last 100 events
        subscriber['click_history'] = subscriber['click_history'][-100:]

        # Recalculate engagement score
        self._calculate_engagement_score(subscriber)
        
        self._save_subscriber_data(email, subscriber)
        return is_unique

    def _calculate_engagement_score(self, subscriber: Dict) -> int:
        """
        Calculate engagement score (0-100) based on behavior.
        
        Factors:
        - Open rate (40% weight)
        - Click rate (40% weight)
        - Recency (20% weight)
        """
        total_sent = subscriber['total_sent']
        
        if total_sent == 0:
            subscriber['engagement_score'] = 0
            subscriber['engagement_level'] = 'no_data'
            return 0

        # Open rate score (0-40 points)
        open_rate = subscriber['unique_opens'] / total_sent
        open_score = open_rate * 40

        # Click rate score (0-40 points)
        click_rate = subscriber['unique_clicks'] / total_sent
        click_score = click_rate * 40

        # Recency score (0-20 points)
        recency_score = 0
        now = datetime.now()
        
        if subscriber['last_click']:
            days_since_click = (now - datetime.fromisoformat(subscriber['last_click'])).days
            if days_since_click <= 7:
                recency_score = 20
            elif days_since_click <= 30:
                recency_score = 15
            elif days_since_click <= 90:
                recency_score = 10
            elif days_since_click <= 180:
                recency_score = 5
        elif subscriber['last_open']:
            days_since_open = (now - datetime.fromisoformat(subscriber['last_open'])).days
            if days_since_open <= 7:
                recency_score = 15
            elif days_since_open <= 30:
                recency_score = 10
            elif days_since_open <= 90:
                recency_score = 5

        total_score = int(open_score + click_score + recency_score)
        subscriber['engagement_score'] = min(total_score, 100)

        # Determine engagement level
        if total_score >= 80:
            subscriber['engagement_level'] = 'highly_engaged'
        elif total_score >= 60:
            subscriber['engagement_level'] = 'engaged'
        elif total_score >= 40:
            subscriber['engagement_level'] = 'moderately_engaged'
        elif total_score >= 20:
            subscriber['engagement_level'] = 'low_engagement'
        else:
            subscriber['engagement_level'] = 'inactive'

        return total_score

    def get_engagement_level(self, email: str) -> str:
        """Get engagement level for a subscriber."""
        subscriber = self._get_subscriber_data(email)
        return subscriber.get('engagement_level', 'unknown')

    def get_subscriber_stats(self, email: str) -> Dict:
        """Get detailed stats for a subscriber."""
        subscriber = self._get_subscriber_data(email)
        
        total_sent = subscriber['total_sent']
        open_rate = (subscriber['unique_opens'] / total_sent * 100) if total_sent > 0 else 0
        click_rate = (subscriber['unique_clicks'] / total_sent * 100) if total_sent > 0 else 0

        return {
            'email': subscriber['email'],
            'engagement_score': subscriber['engagement_score'],
            'engagement_level': subscriber['engagement_level'],
            'total_sent': total_sent,
            'total_opens': subscriber['total_opens'],
            'unique_opens': subscriber['unique_opens'],
            'total_clicks': subscriber['total_clicks'],
            'unique_clicks': subscriber['unique_clicks'],
            'open_rate': round(open_rate, 2),
            'click_rate': round(click_rate, 2),
            'last_sent': subscriber['last_sent'],
            'last_open': subscriber['last_open'],
            'last_click': subscriber['last_click'],
            'first_seen': subscriber['first_seen'],
            'campaigns_participated': len(subscriber['campaigns'])
        }

    def segment_by_engagement(self) -> Dict[str, List[str]]:
        """Segment all subscribers by engagement level."""
        data = self._load_data(self.data_file)
        
        segments = {
            'highly_engaged': [],
            'engaged': [],
            'moderately_engaged': [],
            'low_engagement': [],
            'inactive': [],
            'no_data': []
        }

        for email, subscriber in data.items():
            level = subscriber.get('engagement_level', 'no_data')
            if level in segments:
                segments[level].append(email)

        return segments

    def get_inactive_subscribers(self, days: int = 90) -> List[str]:
        """Get subscribers who haven't engaged in specified days."""
        data = self._load_data(self.data_file)
        cutoff = datetime.now() - timedelta(days=days)
        inactive = []

        for email, subscriber in data.items():
            last_activity = subscriber.get('last_click') or subscriber.get('last_open')
            
            if not last_activity:
                # Never engaged
                if subscriber['total_sent'] > 0:
                    inactive.append(email)
            elif datetime.fromisoformat(last_activity) < cutoff:
                inactive.append(email)

        return inactive

    def get_top_engaged(self, limit: int = 100) -> List[Dict]:
        """Get top engaged subscribers."""
        data = self._load_data(self.data_file)
        
        subscribers = list(data.values())
        subscribers.sort(key=lambda x: x.get('engagement_score', 0), reverse=True)

        return [
            {
                'email': s['email'],
                'engagement_score': s.get('engagement_score', 0),
                'engagement_level': s.get('engagement_level', 'unknown'),
                'open_rate': round((s['unique_opens'] / s['total_sent'] * 100) if s['total_sent'] > 0 else 0, 2),
                'click_rate': round((s['unique_clicks'] / s['total_sent'] * 100) if s['total_sent'] > 0 else 0, 2)
            }
            for s in subscribers[:limit]
        ]

    def get_campaign_stats(self, campaign_id: str) -> Dict:
        """Get statistics for a specific campaign."""
        data = self._load_data(self.data_file)
        
        total_sent = 0
        total_opens = 0
        total_clicks = 0
        unique_opens = 0
        unique_clicks = 0

        for subscriber in data.values():
            if campaign_id in subscriber['campaigns']:
                campaign = subscriber['campaigns'][campaign_id]
                total_sent += 1
                total_opens += campaign.get('open_count', 0)
                total_clicks += campaign.get('click_count', 0)
                if campaign.get('opened'):
                    unique_opens += 1
                if campaign.get('clicked'):
                    unique_clicks += 1

        return {
            'campaign_id': campaign_id,
            'total_sent': total_sent,
            'unique_opens': unique_opens,
            'unique_clicks': unique_clicks,
            'total_opens': total_opens,
            'total_clicks': total_clicks,
            'open_rate': round((unique_opens / total_sent * 100) if total_sent > 0 else 0, 2),
            'click_rate': round((unique_clicks / total_sent * 100) if total_sent > 0 else 0, 2)
        }

    def generate_tracking_pixel(self, email: str, campaign_id: str, base_url: str) -> str:
        """Generate tracking pixel URL for email."""
        token = hashlib.sha256(f"{email}:{campaign_id}:open".encode()).hexdigest()
        return f"{base_url}/track/open?token={token}&email={email}&campaign={campaign_id}"

    def generate_tracking_link(self, email: str, campaign_id: str, 
                               original_url: str, base_url: str) -> str:
        """Generate tracked link URL for email."""
        token = hashlib.sha256(f"{email}:{campaign_id}:click".encode()).hexdigest()
        import urllib.parse
        encoded_url = urllib.parse.quote(original_url)
        return f"{base_url}/track/click?token={token}&email={email}&campaign={campaign_id}&url={encoded_url}"

    def cleanup_old_data(self, days: int = 365) -> int:
        """Remove engagement data older than specified days."""
        data = self._load_data(self.data_file)
        cutoff = datetime.now() - timedelta(days=days)
        removed = 0

        for email in list(data.keys()):
            subscriber = data[email]
            
            # Clean old history
            subscriber['open_history'] = [
                e for e in subscriber.get('open_history', [])
                if datetime.fromisoformat(e['timestamp']) > cutoff
            ]
            subscriber['click_history'] = [
                e for e in subscriber.get('click_history', [])
                if datetime.fromisoformat(e['timestamp']) > cutoff
            ]

            # Remove subscribers with no activity
            if subscriber['total_sent'] == 0 and not subscriber.get('last_open'):
                del data[email]
                removed += 1

        self._save_data(data, self.data_file)
        return removed

    def export_engagement_data(self, output_file: Path):
        """Export engagement data for analysis."""
        data = self._load_data(self.data_file)
        
        export_data = []
        for email, subscriber in data.items():
            export_data.append(self.get_subscriber_stats(email))

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, default=str)


if __name__ == '__main__':
    import sys

    print("=" * 60)
    print("Engagement Tracker")
    print("=" * 60)

    tracker = EngagementTracker()

    if len(sys.argv) < 2:
        print("\nUsage: python engagement_tracker.py <command> [args]")
        print("\nCommands:")
        print("  stats <email>              - Get subscriber stats")
        print("  segment                    - Show engagement segments")
        print("  inactive [days]            - List inactive subscribers")
        print("  top [limit]                - Show top engaged subscribers")
        print("  campaign <id>              - Campaign statistics")
        print("  cleanup [days]             - Remove old data")
        print("  export <file>              - Export data")
        sys.exit(0)

    command = sys.argv[1]

    if command == 'stats' and len(sys.argv) > 2:
        stats = tracker.get_subscriber_stats(sys.argv[2])
        print(f"\nEngagement Stats for: {stats['email']}")
        print("-" * 50)
        print(f"Engagement Score: {stats['engagement_score']}/100")
        print(f"Engagement Level: {stats['engagement_level'].upper()}")
        print(f"Total Sent: {stats['total_sent']}")
        print(f"Unique Opens: {stats['unique_opens']} ({stats['open_rate']}%)")
        print(f"Unique Clicks: {stats['unique_clicks']} ({stats['click_rate']}%)")
        print(f"Campaigns: {stats['campaigns_participated']}")
        print(f"Last Open: {stats['last_open'] or 'Never'}")
        print(f"Last Click: {stats['last_click'] or 'Never'}")
        print()

    elif command == 'segment':
        segments = tracker.segment_by_engagement()
        print("\nEngagement Segments:")
        print("-" * 50)
        for level, emails in segments.items():
            if emails:
                print(f"\n{level.upper()}: {len(emails)}")
                for email in emails[:5]:
                    print(f"  - {email}")
                if len(emails) > 5:
                    print(f"  ... and {len(emails) - 5} more")
        print()

    elif command == 'inactive':
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 90
        inactive = tracker.get_inactive_subscribers(days)
        print(f"\nInactive Subscribers (no activity in {days} days): {len(inactive)}")
        print("-" * 50)
        for email in inactive[:20]:
            print(f"  {email}")
        if len(inactive) > 20:
            print(f"  ... and {len(inactive) - 20} more")
        print()

    elif command == 'top':
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        top = tracker.get_top_engaged(limit)
        print(f"\nTop {len(top)} Engaged Subscribers:")
        print("-" * 50)
        for i, sub in enumerate(top, 1):
            print(f"{i}. {sub['email']} - Score: {sub['engagement_score']} ({sub['engagement_level']})")
        print()

    elif command == 'campaign' and len(sys.argv) > 2:
        stats = tracker.get_campaign_stats(sys.argv[2])
        print(f"\nCampaign Stats: {stats['campaign_id']}")
        print("-" * 50)
        print(f"Sent: {stats['total_sent']}")
        print(f"Open Rate: {stats['open_rate']}%")
        print(f"Click Rate: {stats['click_rate']}%")
        print()

    elif command == 'cleanup':
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 365
        removed = tracker.cleanup_old_data(days)
        print(f"Removed {removed} inactive subscriber records")

    elif command == 'export' and len(sys.argv) > 2:
        tracker.export_engagement_data(Path(sys.argv[2]))
        print(f"Exported engagement data to {sys.argv[2]}")

    else:
        print(f"Unknown command: {command}")
