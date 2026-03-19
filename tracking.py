"""Email Tracking - Open and click tracking with analytics."""
import json
import sqlite3
import hashlib
import secrets
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from urllib.parse import urlparse, parse_qs


class TrackingManager:
    """Track email opens and clicks with unique identifiers."""
    
    def __init__(self, db_path: Path = None):
        if db_path is None:
            db_path = Path(__file__).parent / 'data' / 'tracking.db'
        
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize the tracking database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Campaigns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS campaigns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                template TEXT,
                subject TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_sent INTEGER DEFAULT 0,
                total_opens INTEGER DEFAULT 0,
                total_clicks INTEGER DEFAULT 0
            )
        ''')
        
        # Recipients table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recipients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_id INTEGER,
                email TEXT NOT NULL,
                tracking_id TEXT UNIQUE NOT NULL,
                sent_at TIMESTAMP,
                opened INTEGER DEFAULT 0,
                first_open_at TIMESTAMP,
                last_open_at TIMESTAMP,
                open_count INTEGER DEFAULT 0,
                clicked INTEGER DEFAULT 0,
                first_click_at TIMESTAMP,
                click_count INTEGER DEFAULT 0,
                FOREIGN KEY (campaign_id) REFERENCES campaigns(id)
            )
        ''')
        
        # Clicks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clicks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipient_id INTEGER,
                url TEXT NOT NULL,
                clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_agent TEXT,
                ip_address TEXT,
                FOREIGN KEY (recipient_id) REFERENCES recipients(id)
            )
        ''')
        
        # Opens table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS opens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipient_id INTEGER,
                opened_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_agent TEXT,
                ip_address TEXT,
                FOREIGN KEY (recipient_id) REFERENCES recipients(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def generate_tracking_id(self, email: str) -> str:
        """Generate unique tracking ID for an email."""
        salt = secrets.token_hex(8)
        unique = f"{email}{salt}{datetime.now().isoformat()}"
        return hashlib.sha256(unique.encode()).hexdigest()[:16]
    
    def create_campaign(self, name: str, template: str = None, subject: str = None) -> int:
        """Create a new campaign and return its ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO campaigns (name, template, subject)
            VALUES (?, ?, ?)
        ''', (name, template, subject))
        
        campaign_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return campaign_id
    
    def add_recipient(self, campaign_id: int, email: str) -> str:
        """Add a recipient to a campaign and return tracking ID."""
        tracking_id = self.generate_tracking_id(email)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO recipients (campaign_id, email, tracking_id, sent_at)
            VALUES (?, ?, ?, ?)
        ''', (campaign_id, email, tracking_id, datetime.now()))
        
        conn.commit()
        conn.close()
        
        return tracking_id
    
    def record_open(self, tracking_id: str, user_agent: str = None, ip_address: str = None):
        """Record an email open."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Find recipient
        cursor.execute('SELECT id, open_count FROM recipients WHERE tracking_id = ?', (tracking_id,))
        row = cursor.fetchone()
        
        if row:
            recipient_id, open_count = row
            now = datetime.now()
            
            # Update recipient
            cursor.execute('''
                UPDATE recipients 
                SET opened = 1,
                    first_open_at = COALESCE(first_open_at, ?),
                    last_open_at = ?,
                    open_count = ?
                WHERE id = ?
            ''', (now, now, open_count + 1, recipient_id))
            
            # Record open event
            cursor.execute('''
                INSERT INTO opens (recipient_id, user_agent, ip_address)
                VALUES (?, ?, ?)
            ''', (recipient_id, user_agent, ip_address))
            
            # Update campaign stats
            cursor.execute('''
                UPDATE campaigns SET total_opens = total_opens + 1
                WHERE id = (SELECT campaign_id FROM recipients WHERE id = ?)
            ''', (recipient_id,))
        
        conn.commit()
        conn.close()
    
    def record_click(self, tracking_id: str, url: str, user_agent: str = None, ip_address: str = None):
        """Record a link click."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Find recipient
        cursor.execute('SELECT id, click_count FROM recipients WHERE tracking_id = ?', (tracking_id,))
        row = cursor.fetchone()
        
        if row:
            recipient_id, click_count = row
            now = datetime.now()
            
            # Update recipient
            cursor.execute('''
                UPDATE recipients 
                SET clicked = 1,
                    first_click_at = COALESCE(first_click_at, ?),
                    click_count = ?
                WHERE id = ?
            ''', (now, click_count + 1, recipient_id))
            
            # Record click event
            cursor.execute('''
                INSERT INTO clicks (recipient_id, url, user_agent, ip_address)
                VALUES (?, ?, ?, ?)
            ''', (recipient_id, url, user_agent, ip_address))
            
            # Update campaign stats
            cursor.execute('''
                UPDATE campaigns SET total_clicks = total_clicks + 1
                WHERE id = (SELECT campaign_id FROM recipients WHERE id = ?)
            ''', (recipient_id,))
        
        conn.commit()
        conn.close()
    
    def get_tracking_pixel(self, tracking_id: str) -> str:
        """Generate tracking pixel HTML."""
        # In production, this would point to your server endpoint
        # For now, return a data URI transparent pixel
        pixel_data = (
            'data:image/gif;base64,'
            'R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7'
        )
        return f'<img src="{pixel_data}" width="1" height="1" style="display:none" />'
    
    def add_tracking_pixel(self, html_content: str, tracking_id: str) -> str:
        """Add tracking pixel to HTML content."""
        pixel = self.get_tracking_pixel(tracking_id)
        
        # Insert before closing body tag
        if '</body>' in html_content:
            return html_content.replace('</body>', f'{pixel}\n</body>')
        
        # If no body tag, append at end
        return html_content + pixel
    
    def track_link(self, original_url: str, tracking_id: str) -> str:
        """
        Convert a URL to a tracked link.
        
        In production, this would create a redirect URL on your server.
        For now, we'll encode the tracking info in the URL fragment.
        """
        # Parse original URL
        parsed = urlparse(original_url)
        
        # Add tracking parameter
        params = parse_qs(parsed.query)
        params['tid'] = tracking_id
        params['ts'] = str(int(datetime.now().timestamp()))
        
        # Rebuild URL with tracking
        from urllib.parse import urlencode, urlunparse
        
        new_query = urlencode(params)
        tracked_url = urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            parsed.fragment
        ))
        
        return tracked_url
    
    def track_all_links(self, html_content: str, tracking_id: str) -> str:
        """Find and track all links in HTML content."""
        import re
        
        def replace_link(match):
            full_match = match.group(0)
            href_match = re.search(r'href=["\']([^"\']+)["\']', full_match)
            
            if href_match:
                original_url = href_match.group(1)
                
                # Skip certain URLs
                if original_url.startswith(('#', 'mailto:', 'tel:', 'data:')):
                    return full_match
                if original_url.startswith('unsubscribe') or 'unsubscribe' in original_url:
                    return full_match
                
                # Track the link
                tracked_url = self.track_link(original_url, tracking_id)
                return full_match.replace(original_url, tracked_url)
            
            return full_match
        
        # Find all anchor tags
        return re.sub(r'<a[^>]+href[^>]*>[^<]*</a>', replace_link, html_content, flags=re.IGNORECASE)
    
    def get_campaign_stats(self, campaign_id: int) -> dict:
        """Get statistics for a campaign."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Campaign info
        cursor.execute('SELECT * FROM campaigns WHERE id = ?', (campaign_id,))
        campaign = cursor.fetchone()
        
        if not campaign:
            conn.close()
            return {'error': 'Campaign not found'}
        
        # Recipient stats
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(opened) as opened,
                SUM(clicked) as clicked,
                AVG(open_count) as avg_opens,
                AVG(click_count) as avg_clicks
            FROM recipients WHERE campaign_id = ?
        ''', (campaign_id,))
        stats = cursor.fetchone()
        
        # Top clicked links
        cursor.execute('''
            SELECT url, COUNT(*) as clicks
            FROM clicks
            WHERE recipient_id IN (SELECT id FROM recipients WHERE campaign_id = ?)
            GROUP BY url
            ORDER BY clicks DESC
            LIMIT 10
        ''', (campaign_id,))
        top_links = cursor.fetchall()
        
        conn.close()
        
        total = stats[0] or 1  # Avoid division by zero
        
        return {
            'campaign': {
                'id': campaign[0],
                'name': campaign[1],
                'template': campaign[2],
                'subject': campaign[3],
                'created_at': campaign[4]
            },
            'stats': {
                'total_sent': stats[0],
                'total_opens': stats[1] or 0,
                'total_clicks': stats[2] or 0,
                'open_rate': (stats[1] or 0) / total * 100,
                'click_rate': (stats[2] or 0) / total * 100,
                'avg_opens_per_opened': stats[3] or 0,
                'avg_clicks_per_clicked': stats[4] or 0
            },
            'top_links': [{'url': link[0], 'clicks': link[1]} for link in top_links]
        }
    
    def get_recipient_activity(self, email: str) -> dict:
        """Get activity for a specific recipient."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT r.*, c.name as campaign_name
            FROM recipients r
            JOIN campaigns c ON r.campaign_id = c.id
            WHERE r.email = ?
        ''', (email,))
        recipient = cursor.fetchone()
        
        conn.close()
        
        if not recipient:
            return {'error': 'Recipient not found'}
        
        return {
            'email': recipient[2],
            'tracking_id': recipient[3],
            'campaign': recipient[9],
            'sent_at': recipient[4],
            'opened': bool(recipient[5]),
            'first_open': recipient[6],
            'last_open': recipient[7],
            'open_count': recipient[8],
            'clicked': bool(recipient[9]),
            'first_click': recipient[10],
            'click_count': recipient[11]
        }


# Tracking endpoint handler (for web server integration)
def handle_tracking_request(tracking_id: str, action: str = 'open', url: str = None) -> bool:
    """
    Handle tracking requests from web server.
    
    Usage in web server:
        @app.route('/track/open/<tracking_id>')
        def track_open(tracking_id):
            handle_tracking_request(tracking_id, 'open')
            return Response(status=204)
    """
    manager = TrackingManager()
    
    if action == 'open':
        manager.record_open(tracking_id)
        return True
    elif action == 'click' and url:
        manager.record_click(tracking_id, url)
        return True
    
    return False


if __name__ == '__main__':
    import sys
    
    print("=" * 60)
    print("Email Tracking System")
    print("=" * 60)
    
    manager = TrackingManager()
    
    # Demo
    print("\n📊 Creating demo campaign...")
    campaign_id = manager.create_campaign("Test Campaign", "modern_promo", "Special Offer!")
    print(f"Campaign ID: {campaign_id}")
    
    print("\n📧 Adding recipients...")
    for email in ['user1@example.com', 'user2@example.com', 'user3@example.com']:
        tracking_id = manager.add_recipient(campaign_id, email)
        print(f"  {email} -> Tracking ID: {tracking_id}")
    
    print("\n📈 Campaign Stats:")
    stats = manager.get_campaign_stats(campaign_id)
    print(f"  Total Sent: {stats['stats']['total_sent']}")
    print(f"  Open Rate: {stats['stats']['open_rate']:.1f}%")
    print(f"  Click Rate: {stats['stats']['click_rate']:.1f}%")
    
    print("\n" + "=" * 60)
    print("Tracking system initialized successfully!")
    print("=" * 60)
