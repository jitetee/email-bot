"""Campaign Scheduler - Schedule emails for future delivery."""
import json
import sqlite3
import threading
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Callable
from enum import Enum


class CampaignStatus(Enum):
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CampaignScheduler:
    """Schedule and manage email campaigns for future delivery."""

    def __init__(self, db_path: Path = None):
        if db_path is None:
            db_path = Path(__file__).parent / 'data' / 'scheduler.db'
        
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        self._running = False
        self._scheduler_thread = None

    def _init_db(self):
        """Initialize the scheduler database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Scheduled campaigns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scheduled_campaigns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                template TEXT,
                subject TEXT,
                email_list_file TEXT,
                scheduled_for TIMESTAMP NOT NULL,
                status TEXT DEFAULT 'scheduled',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                total_sent INTEGER DEFAULT 0,
                total_failed INTEGER DEFAULT 0,
                smtp_account TEXT,
                batch_size INTEGER DEFAULT 25,
                delay_min REAL DEFAULT 1.0,
                delay_max REAL DEFAULT 3.0,
                batch_delay INTEGER DEFAULT 30,
                sender_email TEXT,
                sender_name TEXT,
                custom_variables TEXT,
                error_message TEXT
            )
        ''')

        # Campaign execution log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS campaign_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_id INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                event_type TEXT,
                message TEXT,
                FOREIGN KEY (campaign_id) REFERENCES scheduled_campaigns(id)
            )
        ''')

        conn.commit()
        conn.close()

    def schedule_campaign(
        self,
        name: str,
        scheduled_for: datetime,
        template: str,
        subject: str,
        email_list_file: str,
        sender_email: str,
        sender_name: str = "Your Company",
        smtp_account: str = None,
        batch_size: int = 25,
        delay_min: float = 1.0,
        delay_max: float = 3.0,
        batch_delay: int = 30,
        custom_variables: dict = None
    ) -> int:
        """
        Schedule a new campaign for future delivery.

        Args:
            name: Campaign name
            scheduled_for: When to send the campaign
            template: Template name to use
            subject: Email subject line
            email_list_file: Path to email list file
            sender_email: Sender email address
            sender_name: Sender name
            smtp_account: SMTP account to use (for multi-SMTP setups)
            batch_size: Emails per batch
            delay_min: Minimum delay between emails
            delay_max: Maximum delay between emails
            batch_delay: Delay between batches
            custom_variables: JSON string of custom template variables

        Returns:
            Campaign ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO scheduled_campaigns (
                name, template, subject, email_list_file, scheduled_for,
                sender_email, sender_name, smtp_account, batch_size,
                delay_min, delay_max, batch_delay, custom_variables
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            name, template, subject, email_list_file, scheduled_for.isoformat(),
            sender_email, sender_name, smtp_account, batch_size,
            delay_min, delay_max, batch_delay, json.dumps(custom_variables or {})
        ))

        campaign_id = cursor.lastrowid
        
        self._log_event(campaign_id, 'scheduled', f'Campaign scheduled for {scheduled_for}')
        
        conn.commit()
        conn.close()

        return campaign_id

    def get_campaign(self, campaign_id: int) -> Optional[dict]:
        """Get campaign details by ID."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM scheduled_campaigns WHERE id = ?', (campaign_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return dict(row)
        return None

    def get_all_campaigns(self, status: str = None, limit: int = 50) -> List[dict]:
        """Get all campaigns, optionally filtered by status."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if status:
            cursor.execute(
                'SELECT * FROM scheduled_campaigns WHERE status = ? ORDER BY scheduled_for DESC LIMIT ?',
                (status, limit)
            )
        else:
            cursor.execute(
                'SELECT * FROM scheduled_campaigns ORDER BY scheduled_for DESC LIMIT ?',
                (limit,)
            )

        campaigns = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return campaigns

    def get_due_campaigns(self) -> List[dict]:
        """Get campaigns that are due to be sent."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        now = datetime.now().isoformat()
        cursor.execute('''
            SELECT * FROM scheduled_campaigns 
            WHERE scheduled_for <= ? AND status = 'scheduled'
            ORDER BY scheduled_for ASC
        ''', (now,))

        campaigns = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return campaigns

    def update_status(self, campaign_id: int, status: CampaignStatus, error_message: str = None):
        """Update campaign status."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        updates = ['status = ?']
        params = [status.value]

        if status == CampaignStatus.RUNNING:
            updates.append('started_at = CURRENT_TIMESTAMP')
        elif status in (CampaignStatus.COMPLETED, CampaignStatus.FAILED, CampaignStatus.CANCELLED):
            updates.append('completed_at = CURRENT_TIMESTAMP')

        if error_message:
            updates.append('error_message = ?')
            params.append(error_message)

        params.append(campaign_id)

        cursor.execute(f'''
            UPDATE scheduled_campaigns 
            SET {', '.join(updates)}
            WHERE id = ?
        ''', params)

        self._log_event(campaign_id, 'status_change', f'Status changed to {status.value}')

        conn.commit()
        conn.close()

    def update_stats(self, campaign_id: int, sent: int, failed: int):
        """Update campaign sending statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE scheduled_campaigns 
            SET total_sent = ?, total_failed = ?
            WHERE id = ?
        ''', (sent, failed, campaign_id))

        conn.commit()
        conn.close()

    def cancel_campaign(self, campaign_id: int) -> bool:
        """Cancel a scheduled campaign."""
        campaign = self.get_campaign(campaign_id)
        
        if not campaign:
            return False
        
        if campaign['status'] != 'scheduled':
            return False  # Can only cancel scheduled campaigns

        self.update_status(campaign_id, CampaignStatus.CANCELLED)
        return True

    def delete_campaign(self, campaign_id: int) -> bool:
        """Delete a campaign from the scheduler."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('DELETE FROM scheduled_campaigns WHERE id = ?', (campaign_id,))
        cursor.execute('DELETE FROM campaign_logs WHERE campaign_id = ?', (campaign_id,))

        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()

        return deleted

    def _log_event(self, campaign_id: int, event_type: str, message: str):
        """Log a campaign event."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO campaign_logs (campaign_id, event_type, message)
            VALUES (?, ?, ?)
        ''', (campaign_id, event_type, message))

        conn.commit()
        conn.close()

    def get_campaign_logs(self, campaign_id: int) -> List[dict]:
        """Get logs for a specific campaign."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            'SELECT * FROM campaign_logs WHERE campaign_id = ? ORDER BY timestamp DESC',
            (campaign_id,)
        )

        logs = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return logs

    def start_scheduler(self, send_callback: Callable = None):
        """
        Start the background scheduler thread.

        Args:
            send_callback: Function to call when a campaign is due.
                          Receives campaign dict as argument.
        """
        if self._running:
            return

        self._running = True
        self._send_callback = send_callback
        self._scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self._scheduler_thread.start()

    def stop_scheduler(self):
        """Stop the background scheduler."""
        self._running = False
        if self._scheduler_thread:
            self._scheduler_thread.join(timeout=5)

    def _scheduler_loop(self):
        """Main scheduler loop - checks for due campaigns."""
        while self._running:
            try:
                due_campaigns = self.get_due_campaigns()

                for campaign in due_campaigns:
                    if self._send_callback:
                        self._log_event(campaign['id'], 'triggered', 'Campaign triggered for sending')
                        self._send_callback(campaign)

                # Check every 30 seconds
                time.sleep(30)

            except Exception as e:
                print(f"Scheduler error: {e}")
                time.sleep(30)

    def get_statistics(self) -> dict:
        """Get scheduler statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        stats = {}

        # Count by status
        cursor.execute('''
            SELECT status, COUNT(*) as count 
            FROM scheduled_campaigns 
            GROUP BY status
        ''')
        stats['by_status'] = {row[0]: row[1] for row in cursor.fetchall()}

        # Total campaigns
        cursor.execute('SELECT COUNT(*) FROM scheduled_campaigns')
        stats['total'] = cursor.fetchone()[0]

        # Upcoming campaigns
        cursor.execute('''
            SELECT COUNT(*) FROM scheduled_campaigns 
            WHERE scheduled_for > datetime('now') AND status = 'scheduled'
        ''')
        stats['upcoming'] = cursor.fetchone()[0]

        # Overdue campaigns
        cursor.execute('''
            SELECT COUNT(*) FROM scheduled_campaigns 
            WHERE scheduled_for < datetime('now') AND status = 'scheduled'
        ''')
        stats['overdue'] = cursor.fetchone()[0]

        conn.close()

        return stats

    def reschedule_campaign(
        self, 
        campaign_id: int, 
        new_time: datetime,
        reason: str = None
    ) -> bool:
        """Reschedule a campaign to a new time."""
        campaign = self.get_campaign(campaign_id)
        
        if not campaign:
            return False
        
        if campaign['status'] != 'scheduled':
            return False  # Can only reschedule pending campaigns

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE scheduled_campaigns 
            SET scheduled_for = ?
            WHERE id = ?
        ''', (new_time.isoformat(), campaign_id))

        self._log_event(
            campaign_id, 
            'rescheduled', 
            f'Rescheduled from {campaign["scheduled_for"]} to {new_time}. Reason: {reason or "N/A"}'
        )

        conn.commit()
        conn.close()

        return True


class SchedulerManager:
    """High-level manager for the campaign scheduler."""

    def __init__(self):
        self.scheduler = CampaignScheduler()
        self._campaign_handlers = {}

    def register_handler(self, campaign_id: int, handler: Callable):
        """Register a handler function for a specific campaign."""
        self._campaign_handlers[campaign_id] = handler

    def schedule(
        self,
        name: str,
        send_at: datetime,
        template: str,
        subject: str,
        email_list: str,
        sender_email: str,
        **kwargs
    ) -> int:
        """
        Schedule a new campaign.

        Args:
            name: Campaign name
            send_at: When to send
            template: Template name
            subject: Email subject
            email_list: Path to email list
            sender_email: Sender email
            **kwargs: Additional options (sender_name, batch_size, etc.)

        Returns:
            Campaign ID
        """
        return self.scheduler.schedule_campaign(
            name=name,
            scheduled_for=send_at,
            template=template,
            subject=subject,
            email_list_file=email_list,
            sender_email=sender_email,
            **kwargs
        )

    def schedule_in(self, name: str, minutes: int, **kwargs) -> int:
        """Schedule a campaign to run in N minutes."""
        send_at = datetime.now() + timedelta(minutes=minutes)
        return self.schedule(name, send_at, **kwargs)

    def schedule_tomorrow(self, name: str, hour: int = 9, minute: int = 0, **kwargs) -> int:
        """Schedule a campaign for tomorrow at specified time."""
        tomorrow = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
        tomorrow += timedelta(days=1)
        return self.schedule(name, tomorrow, **kwargs)

    def list_upcoming(self, limit: int = 20) -> List[dict]:
        """List upcoming scheduled campaigns."""
        return self.scheduler.get_all_campaigns(status='scheduled', limit=limit)

    def cancel(self, campaign_id: int) -> bool:
        """Cancel a scheduled campaign."""
        return self.scheduler.cancel_campaign(campaign_id)

    def get_stats(self) -> dict:
        """Get scheduler statistics."""
        return self.scheduler.get_statistics()


if __name__ == '__main__':
    import sys

    print("=" * 60)
    print("Campaign Scheduler")
    print("=" * 60)

    scheduler = CampaignScheduler()

    if len(sys.argv) < 2:
        print("\nUsage: python campaign_scheduler.py <command> [args]")
        print("\nCommands:")
        print("  list                  - List all scheduled campaigns")
        print("  stats                 - Show scheduler statistics")
        print("  cancel <id>           - Cancel a scheduled campaign")
        print("  demo                  - Create a demo scheduled campaign")
        print("  run                   - Start the scheduler (background)")
        sys.exit(0)

    command = sys.argv[1]

    if command == 'list':
        campaigns = scheduler.get_all_campaigns()
        if not campaigns:
            print("\nNo scheduled campaigns")
        else:
            print(f"\n{'ID':<6} {'Name':<25} {'Scheduled For':<20} {'Status':<12}")
            print("-" * 65)
            for c in campaigns:
                print(f"{c['id']:<6} {c['name']:<25} {c['scheduled_for'][:16]:<20} {c['status']:<12}")

    elif command == 'stats':
        stats = scheduler.get_statistics()
        print(f"\nScheduler Statistics:")
        print(f"  Total Campaigns: {stats.get('total', 0)}")
        print(f"  Scheduled: {stats.get('by_status', {}).get('scheduled', 0)}")
        print(f"  Running: {stats.get('by_status', {}).get('running', 0)}")
        print(f"  Completed: {stats.get('by_status', {}).get('completed', 0)}")
        print(f"  Failed: {stats.get('by_status', {}).get('failed', 0)}")
        print(f"  Upcoming: {stats.get('upcoming', 0)}")
        print(f"  Overdue: {stats.get('overdue', 0)}")

    elif command == 'cancel' and len(sys.argv) > 2:
        campaign_id = int(sys.argv[2])
        if scheduler.cancel_campaign(campaign_id):
            print(f"✓ Campaign {campaign_id} cancelled")
        else:
            print(f"✗ Failed to cancel campaign {campaign_id}")

    elif command == 'demo':
        # Create a demo campaign scheduled for 1 minute from now
        demo_time = datetime.now() + timedelta(minutes=1)
        campaign_id = scheduler.schedule_campaign(
            name="Demo Campaign",
            scheduled_for=demo_time,
            template="modern_promo",
            subject="Special Offer!",
            email_list_file="data/email_list.txt",
            sender_email="demo@example.com",
            sender_name="Demo Company"
        )
        print(f"\n✓ Demo campaign scheduled!")
        print(f"  Campaign ID: {campaign_id}")
        print(f"  Scheduled for: {demo_time}")
        print(f"  Run 'list' to see all scheduled campaigns")

    elif command == 'run':
        print("\nStarting scheduler... Press Ctrl+C to stop")
        
        def on_campaign_due(campaign):
            print(f"\n🔔 Campaign Due: {campaign['name']} (ID: {campaign['id']})")
            print(f"   Template: {campaign['template']}")
            print(f"   Subject: {campaign['subject']}")
            # In production, this would trigger the actual email sending
        
        scheduler.start_scheduler(send_callback=on_campaign_due)
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping scheduler...")
            scheduler.stop_scheduler()
            print("Scheduler stopped")

    else:
        print(f"Unknown command: {command}")
        print("Run without arguments to see usage")
