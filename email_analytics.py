"""Email Analytics Tracker - Track opens, clicks, bounces, and engagement."""
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta


class EmailAnalytics:
    """Track and analyze email campaign performance."""

    def __init__(self, data_file: Path = None):
        self.data_file = data_file or Path(__file__).parent / 'data' / 'email_analytics.json'
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Create data file if it doesn't exist."""
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.data_file.exists():
            self._save_data({'campaigns': {}, 'emails': {}})

    def _load_data(self) -> Dict:
        """Load data from JSON file."""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {'campaigns': {}, 'emails': {}}

    def _save_data(self, data: Dict):
        """Save data to JSON file."""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)

    def track_email_sent(self, campaign_id: str, email: str, subject: str = ""):
        """Track when an email is sent."""
        data = self._load_data()
        
        # Initialize campaign if not exists
        if campaign_id not in data['campaigns']:
            data['campaigns'][campaign_id] = {
                'created_at': datetime.now().isoformat(),
                'subject': subject,
                'sent': 0,
                'opened': 0,
                'clicked': 0,
                'bounced': 0,
                'unsubscribed': 0
            }
        
        # Track email
        email_key = f"{campaign_id}:{email}"
        data['emails'][email_key] = {
            'campaign_id': campaign_id,
            'email': email,
            'sent_at': datetime.now().isoformat(),
            'opened': False,
            'opened_at': None,
            'clicked': False,
            'clicked_at': None,
            'bounce': False,
            'unsubscribed': False,
            'open_count': 0,
            'click_count': 0,
            'device': None,
            'location': None
        }
        
        data['campaigns'][campaign_id]['sent'] += 1
        self._save_data(data)

    def track_open(self, campaign_id: str, email: str, 
                   user_agent: str = None, ip: str = None) -> bool:
        """Track email open."""
        data = self._load_data()
        email_key = f"{campaign_id}:{email}"
        
        if email_key not in data['emails']:
            return False
        
        email_data = data['emails'][email_key]
        is_first_open = not email_data['opened']
        
        email_data['opened'] = True
        email_data['opened_at'] = datetime.now().isoformat()
        email_data['open_count'] += 1
        
        if user_agent:
            email_data['device'] = self._detect_device(user_agent)
        if ip:
            email_data['location'] = self._detect_location(ip)
        
        # Update campaign stats
        if is_first_open:
            data['campaigns'][campaign_id]['opened'] += 1
        
        self._save_data(data)
        return is_first_open

    def track_click(self, campaign_id: str, email: str, url: str,
                   user_agent: str = None, ip: str = None) -> bool:
        """Track link click."""
        data = self._load_data()
        email_key = f"{campaign_id}:{email}"
        
        if email_key not in data['emails']:
            return False
        
        email_data = data['emails'][email_key]
        is_first_click = not email_data['clicked']
        
        email_data['clicked'] = True
        email_data['clicked_at'] = datetime.now().isoformat()
        email_data['click_count'] += 1
        
        if user_agent:
            email_data['device'] = self._detect_device(user_agent)
        
        # Update campaign stats
        if is_first_click:
            data['campaigns'][campaign_id]['clicked'] += 1
        
        self._save_data(data)
        return is_first_click

    def track_bounce(self, campaign_id: str, email: str, 
                    bounce_type: str = "hard") -> bool:
        """Track email bounce."""
        data = self._load_data()
        email_key = f"{campaign_id}:{email}"
        
        if email_key not in data['emails']:
            return False
        
        email_data = data['emails'][email_key]
        email_data['bounce'] = True
        email_data['bounce_type'] = bounce_type
        email_data['bounced_at'] = datetime.now().isoformat()
        
        # Update campaign stats
        data['campaigns'][campaign_id]['bounced'] += 1
        
        self._save_data(data)
        return True

    def track_unsubscribe(self, campaign_id: str, email: str) -> bool:
        """Track unsubscribe."""
        data = self._load_data()
        email_key = f"{campaign_id}:{email}"
        
        if email_key not in data['emails']:
            return False
        
        email_data = data['emails'][email_key]
        email_data['unsubscribed'] = True
        email_data['unsubscribed_at'] = datetime.now().isoformat()
        
        # Update campaign stats
        data['campaigns'][campaign_id]['unsubscribed'] += 1
        
        self._save_data(data)
        return True

    def _detect_device(self, user_agent: str) -> str:
        """Detect device type from user agent."""
        ua = user_agent.lower()
        
        if 'mobile' in ua or 'android' in ua or 'iphone' in ua:
            return 'mobile'
        elif 'tablet' in ua or 'ipad' in ua:
            return 'tablet'
        else:
            return 'desktop'

    def _detect_location(self, ip: str) -> str:
        """Detect location from IP (simplified)."""
        # In production, use IP geolocation API
        return 'Unknown'

    def get_campaign_stats(self, campaign_id: str) -> Dict:
        """Get statistics for a campaign."""
        data = self._load_data()
        
        if campaign_id not in data['campaigns']:
            return {'error': 'Campaign not found'}
        
        campaign = data['campaigns'][campaign_id]
        sent = campaign['sent']
        
        return {
            'campaign_id': campaign_id,
            'subject': campaign.get('subject', ''),
            'sent': sent,
            'opened': campaign['opened'],
            'clicked': campaign['clicked'],
            'bounced': campaign['bounced'],
            'unsubscribed': campaign['unsubscribed'],
            'open_rate': round((campaign['opened'] / sent * 100) if sent > 0 else 0, 2),
            'click_rate': round((campaign['clicked'] / sent * 100) if sent > 0 else 0, 2),
            'bounce_rate': round((campaign['bounced'] / sent * 100) if sent > 0 else 0, 2),
            'unsubscribe_rate': round((campaign['unsubscribed'] / sent * 100) if sent > 0 else 0, 2)
        }

    def get_all_campaigns(self) -> List[Dict]:
        """Get all campaigns with stats."""
        campaigns = []
        
        for campaign_id, campaign_data in self._load_data()['campaigns'].items():
            stats = self.get_campaign_stats(campaign_id)
            campaigns.append(stats)
        
        campaigns.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return campaigns

    def get_device_breakdown(self, campaign_id: str) -> Dict:
        """Get device breakdown for campaign."""
        data = self._load_data()
        devices = {'mobile': 0, 'tablet': 0, 'desktop': 0, 'unknown': 0}
        
        for email_key, email_data in data['emails'].items():
            if email_data['campaign_id'] == campaign_id and email_data['opened']:
                device = email_data.get('device', 'unknown')
                if device in devices:
                    devices[device] += 1
                else:
                    devices['unknown'] += 1
        
        return devices

    def get_time_analysis(self, campaign_id: str) -> Dict:
        """Get time-based analysis."""
        data = self._load_data()
        
        hours = {str(i): 0 for i in range(24)}
        days = {'Monday': 0, 'Tuesday': 0, 'Wednesday': 0, 
                'Thursday': 0, 'Friday': 0, 'Saturday': 0, 'Sunday': 0}
        
        for email_key, email_data in data['emails'].items():
            if email_data['campaign_id'] == campaign_id and email_data['opened_at']:
                try:
                    dt = datetime.fromisoformat(email_data['opened_at'])
                    hours[str(dt.hour)] += 1
                    days[dt.strftime('%A')] += 1
                except:
                    pass
        
        return {
            'by_hour': hours,
            'by_day': days,
            'best_hour': max(hours, key=hours.get) if any(hours.values()) else 'N/A',
            'best_day': max(days, key=days.get) if any(days.values()) else 'N/A'
        }


if __name__ == '__main__':
    import sys

    analytics = EmailAnalytics()

    print("=" * 60)
    print("Email Analytics Tracker")
    print("=" * 60)

    if len(sys.argv) < 2:
        print("\nUsage: python email_analytics.py <command> [args]")
        print("\nCommands:")
        print("  campaigns               - List all campaigns")
        print("  stats <campaign_id>     - Get campaign statistics")
        print("  devices <campaign>      - Get device breakdown")
        print("  time <campaign>         - Get time analysis")
        sys.exit(0)

    command = sys.argv[1]

    if command == 'campaigns':
        campaigns = analytics.get_all_campaigns()
        print(f"\nCampaigns ({len(campaigns)}):")
        for camp in campaigns[:10]:
            print(f"\n  Campaign: {camp['campaign_id']}")
            print(f"  Sent: {camp['sent']}, Opened: {camp['opened']}, Clicked: {camp['clicked']}")
            print(f"  Open Rate: {camp['open_rate']}%")

    elif command == 'stats' and len(sys.argv) > 2:
        stats = analytics.get_campaign_stats(sys.argv[2])
        print(f"\nCampaign Statistics: {sys.argv[2]}")
        print("=" * 60)
        print(f"Sent: {stats['sent']}")
        print(f"Opened: {stats['opened']} ({stats['open_rate']}%)")
        print(f"Clicked: {stats['clicked']} ({stats['click_rate']}%)")
        print(f"Bounced: {stats['bounced']} ({stats['bounce_rate']}%)")

    elif command == 'devices' and len(sys.argv) > 2:
        devices = analytics.get_device_breakdown(sys.argv[2])
        print(f"\nDevice Breakdown: {sys.argv[2]}")
        for device, count in devices.items():
            if count > 0:
                print(f"  {device}: {count}")

    elif command == 'time' and len(sys.argv) > 2:
        time_data = analytics.get_time_analysis(sys.argv[2])
        print(f"\nTime Analysis: {sys.argv[2]}")
        print(f"Best Hour: {time_data['best_hour']}:00")
        print(f"Best Day: {time_data['best_day']}")

    else:
        print(f"Unknown command: {command}")
