"""Email List Segmentation Tool - Segment subscribers by various criteria."""
import json
from pathlib import Path
from typing import Dict, List, Callable
from datetime import datetime, timedelta


class EmailSegmenter:
    """Segment email lists based on various criteria."""

    def __init__(self, email_list_file: Path = None, subscribers_file: Path = None):
        self.email_list_file = email_list_file or Path(__file__).parent / 'data' / 'email_list.txt'
        self.subscribers_file = subscribers_file or Path(__file__).parent / 'data' / 'subscribers.json'
        self.engagement_file = Path(__file__).parent / 'data' / 'engagement.json'

    def load_email_list(self) -> List[str]:
        """Load basic email list."""
        if not self.email_list_file.exists():
            return []
        
        emails = []
        with open(self.email_list_file, 'r', encoding='utf-8') as f:
            for line in f:
                email = line.strip()
                if email and not email.startswith('#') and '@' in email:
                    emails.append(email.lower())
        return emails

    def load_subscribers(self) -> List[Dict]:
        """Load subscribers with custom fields."""
        if not self.subscribers_file.exists():
            return []
        
        try:
            with open(self.subscribers_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []

    def load_engagement(self) -> Dict:
        """Load engagement data."""
        if not self.engagement_file.exists():
            return {}
        
        try:
            with open(self.engagement_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}

    def segment_by_domain(self) -> Dict[str, List[str]]:
        """Segment emails by domain (gmail.com, yahoo.com, etc.)."""
        emails = self.load_email_list()
        segments = {}
        
        for email in emails:
            try:
                domain = email.split('@')[1]
                if domain not in segments:
                    segments[domain] = []
                segments[domain].append(email)
            except:
                pass
        
        return segments

    def segment_by_engagement(self) -> Dict[str, List[str]]:
        """Segment by engagement level."""
        engagement = self.load_engagement()
        segments = {
            'highly_engaged': [],
            'engaged': [],
            'moderately_engaged': [],
            'low_engagement': [],
            'inactive': [],
            'no_data': []
        }
        
        for email, data in engagement.items():
            score = data.get('engagement_score', 0)
            level = data.get('engagement_level', 'no_data')
            
            if level in segments:
                segments[level].append(email)
            else:
                # Classify by score
                if score >= 80:
                    segments['highly_engaged'].append(email)
                elif score >= 60:
                    segments['engaged'].append(email)
                elif score >= 40:
                    segments['moderately_engaged'].append(email)
                elif score >= 20:
                    segments['low_engagement'].append(email)
                else:
                    segments['inactive'].append(email)
        
        return segments

    def segment_by_signup_date(self, period: str = 'month') -> Dict[str, List[str]]:
        """Segment by signup date."""
        subscribers = self.load_subscribers()
        segments = {}
        now = datetime.now()
        
        for sub in subscribers:
            try:
                subscribed_at = datetime.fromisoformat(sub['subscribed_at'])
                
                if period == 'week':
                    key = subscribed_at.strftime('%Y-W%W')
                elif period == 'month':
                    key = subscribed_at.strftime('%Y-%m')
                elif period == 'quarter':
                    quarter = (subscribed_at.month - 1) // 3 + 1
                    key = f"{subscribed_at.year}-Q{quarter}"
                elif period == 'year':
                    key = str(subscribed_at.year)
                else:
                    key = subscribed_at.strftime('%Y-%m')
                
                if key not in segments:
                    segments[key] = []
                segments[key].append(sub['email'])
            except:
                pass
        
        # Sort by key
        return dict(sorted(segments.items(), reverse=True))

    def segment_by_location(self) -> Dict[str, List[str]]:
        """Segment by location (if available in custom fields)."""
        subscribers = self.load_subscribers()
        segments = {}
        
        for sub in subscribers:
            location = sub.get('location', 'Unknown')
            if not location:
                location = 'Unknown'
            
            if location not in segments:
                segments[location] = []
            segments[location].append(sub['email'])
        
        return segments

    def segment_by_tags(self) -> Dict[str, List[str]]:
        """Segment by tags."""
        subscribers = self.load_subscribers()
        segments = {}
        
        for sub in subscribers:
            tags = sub.get('tags', [])
            if not tags:
                tags = ['untagged']
            
            for tag in tags:
                if tag not in segments:
                    segments[tag] = []
                segments[tag].append(sub['email'])
        
        return segments

    def segment_by_custom_field(self, field: str) -> Dict[str, List[str]]:
        """Segment by any custom field."""
        subscribers = self.load_subscribers()
        segments = {}
        
        for sub in subscribers:
            value = sub.get(field, '(not set)')
            if not value:
                value = '(not set)'
            
            value = str(value)
            if value not in segments:
                segments[value] = []
            segments[value].append(sub['email'])
        
        return segments

    def segment_by_activity(self, days: int = 30) -> Dict[str, List[str]]:
        """Segment by recent activity."""
        engagement = self.load_engagement()
        now = datetime.now()
        cutoff = now - timedelta(days=days)
        
        segments = {
            'active': [],
            'inactive': [],
            'never_active': []
        }
        
        for email, data in engagement.items():
            last_activity = data.get('last_click') or data.get('last_open')
            
            if not last_activity:
                if data.get('total_sent', 0) > 0:
                    segments['never_active'].append(email)
                else:
                    segments['inactive'].append(email)
            else:
                try:
                    activity_date = datetime.fromisoformat(last_activity)
                    if activity_date >= cutoff:
                        segments['active'].append(email)
                    else:
                        segments['inactive'].append(email)
                except:
                    segments['inactive'].append(email)
        
        return segments

    def segment_advanced(self, filters: Dict) -> List[str]:
        """
        Advanced segmentation with multiple filters.
        
        Args:
            filters: Dict with filter criteria
                - engagement_min: Minimum engagement score
                - engagement_max: Maximum engagement score
                - tags: List of required tags
                - domain: Email domain
                - location: Location
                - active_days: Active in last N days
        
        Returns:
            List of matching emails
        """
        subscribers = self.load_subscribers()
        engagement = self.load_engagement()
        results = []
        
        for sub in subscribers:
            email = sub['email']
            match = True
            
            # Filter by domain
            if 'domain' in filters:
                email_domain = email.split('@')[1] if '@' in email else ''
                if email_domain != filters['domain']:
                    match = False
            
            # Filter by tags
            if 'tags' in filters:
                sub_tags = sub.get('tags', [])
                for tag in filters['tags']:
                    if tag not in sub_tags:
                        match = False
                        break
            
            # Filter by location
            if 'location' in filters and match:
                if sub.get('location') != filters['location']:
                    match = False
            
            # Filter by engagement score
            if ('engagement_min' in filters or 'engagement_max' in filters) and match:
                eng_data = engagement.get(email, {})
                score = eng_data.get('engagement_score', 0)
                
                if 'engagement_min' in filters and score < filters['engagement_min']:
                    match = False
                if 'engagement_max' in filters and score > filters['engagement_max']:
                    match = False
            
            # Filter by recent activity
            if 'active_days' in filters and match:
                eng_data = engagement.get(email, {})
                last_activity = eng_data.get('last_click') or eng_data.get('last_open')
                
                if last_activity:
                    try:
                        activity_date = datetime.fromisoformat(last_activity)
                        cutoff = datetime.now() - timedelta(days=filters['active_days'])
                        if activity_date < cutoff:
                            match = False
                    except:
                        match = False
                else:
                    match = False
            
            if match:
                results.append(email)
        
        return results

    def get_segment_statistics(self) -> Dict:
        """Get statistics for all segments."""
        return {
            'by_domain': {k: len(v) for k, v in self.segment_by_domain().items()},
            'by_engagement': {k: len(v) for k, v in self.segment_by_engagement().items()},
            'by_signup': {k: len(v) for k, v in self.segment_by_signup_date().items()},
            'by_tags': {k: len(v) for k, v in self.segment_by_tags().items()},
            'by_activity_30d': {k: len(v) for k, v in self.segment_by_activity(30).items()}
        }

    def export_segment(self, emails: List[str], output_file: Path):
        """Export segment to file."""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# Email Segment - {len(emails)} emails\n")
            f.write(f"# Generated: {datetime.now().isoformat()}\n\n")
            for email in sorted(emails):
                f.write(f"{email}\n")


if __name__ == '__main__':
    import sys

    segmenter = EmailSegmenter()

    print("=" * 60)
    print("Email List Segmentation Tool")
    print("=" * 60)

    if len(sys.argv) < 2:
        print("\nUsage: python email_segmenter.py <command> [args]")
        print("\nCommands:")
        print("  domain           - Segment by domain")
        print("  engagement       - Segment by engagement")
        print("  signup [period]  - Segment by signup date (week/month/quarter/year)")
        print("  location         - Segment by location")
        print("  tags             - Segment by tags")
        print("  activity [days]  - Segment by activity")
        print("  stats            - Show all segment statistics")
        print("  export <file>    - Export segment")
        sys.exit(0)

    command = sys.argv[1]

    if command == 'domain':
        segments = segmenter.segment_by_domain()
        print(f"\nSegments by Domain ({len(segments)} domains):")
        for domain, emails in sorted(segments.items(), key=lambda x: -len(x[1])):
            print(f"  {domain}: {len(emails)} emails")
            for email in emails[:5]:
                print(f"    - {email}")
            if len(emails) > 5:
                print(f"    ... and {len(emails) - 5} more")

    elif command == 'engagement':
        segments = segmenter.segment_by_engagement()
        print(f"\nSegments by Engagement:")
        for level, emails in segments.items():
            print(f"  {level}: {len(emails)} emails")

    elif command == 'signup':
        period = sys.argv[2] if len(sys.argv) > 2 else 'month'
        segments = segmenter.segment_by_signup_date(period)
        print(f"\nSegments by Signup Date ({period}):")
        for period, emails in list(segments.items())[:10]:
            print(f"  {period}: {len(emails)} emails")

    elif command == 'location':
        segments = segmenter.segment_by_location()
        print(f"\nSegments by Location:")
        for location, emails in sorted(segments.items(), key=lambda x: -len(x[1])):
            print(f"  {location}: {len(emails)} emails")

    elif command == 'tags':
        segments = segmenter.segment_by_tags()
        print(f"\nSegments by Tags:")
        for tag, emails in sorted(segments.items(), key=lambda x: -len(x[1])):
            print(f"  {tag}: {len(emails)} emails")

    elif command == 'activity':
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        segments = segmenter.segment_by_activity(days)
        print(f"\nSegments by Activity (last {days} days):")
        for level, emails in segments.items():
            print(f"  {level}: {len(emails)} emails")

    elif command == 'stats':
        stats = segmenter.get_segment_statistics()
        print("\nSegment Statistics:")
        print("=" * 60)
        for segment_type, data in stats.items():
            print(f"\n{segment_type.upper()}:")
            for key, count in list(data.items())[:10]:
                print(f"  {key}: {count}")

    elif command == 'export' and len(sys.argv) > 2:
        emails = segmenter.load_email_list()
        segmenter.export_segment(emails, Path(sys.argv[2]))
        print(f"✓ Exported {len(emails)} emails to {sys.argv[2]}")

    else:
        print(f"Unknown command: {command}")
