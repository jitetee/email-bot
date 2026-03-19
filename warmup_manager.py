"""Warm-up Mode - Gradually increase sending volume to build sender reputation."""
import sqlite3
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from enum import Enum


class WarmupPhase(Enum):
    """Warm-up phases with recommended daily limits."""
    PHASE_1 = ("phase_1", "Days 1-3: Starting slow", 20, 1.0, 3.0)
    PHASE_2 = ("phase_2", "Days 4-7: Building up", 50, 1.5, 4.0)
    PHASE_3 = ("phase_3", "Days 8-14: Moderate volume", 100, 2.0, 5.0)
    PHASE_4 = ("phase_4", "Days 15-21: Near normal", 250, 2.0, 5.0)
    PHASE_5 = ("phase_5", "Days 22+: Full volume", 500, 1.0, 3.0)
    
    def __init__(self, code: str, description: str, daily_limit: int, delay_min: float, delay_max: float):
        self.code = code
        self.description = description
        self.daily_limit = daily_limit
        self.delay_min = delay_min
        self.delay_max = delay_max


class WarmupManager:
    """Manage email account warm-up process."""

    def __init__(self, db_path: Path = None):
        if db_path is None:
            db_path = Path(__file__).parent / 'data' / 'warmup.db'
        
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize the warmup tracking database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Warmup sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS warmup_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                start_date DATE NOT NULL,
                status TEXT DEFAULT 'active',
                current_phase TEXT DEFAULT 'phase_1',
                current_day INTEGER DEFAULT 1,
                total_sent INTEGER DEFAULT 0,
                total_failed INTEGER DEFAULT 0,
                target_daily_limit INTEGER DEFAULT 20,
                completed_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT
            )
        ''')

        # Daily warmup logs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS warmup_daily_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                date DATE NOT NULL,
                phase TEXT,
                emails_sent INTEGER DEFAULT 0,
                emails_failed INTEGER DEFAULT 0,
                avg_delay REAL,
                bounce_count INTEGER DEFAULT 0,
                complaint_count INTEGER DEFAULT 0,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES warmup_sessions(id)
            )
        ''')

        # Warmup recommendations
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS warmup_recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                day INTEGER NOT NULL,
                phase TEXT NOT NULL,
                recommended_limit INTEGER NOT NULL,
                recommended_delay_min REAL NOT NULL,
                recommended_delay_max REAL NOT NULL,
                tips TEXT
            )
        ''')

        # Insert default recommendations
        cursor.execute('SELECT COUNT(*) FROM warmup_recommendations')
        if cursor.fetchone()[0] == 0:
            self._insert_default_recommendations(cursor)

        conn.commit()
        conn.close()

    def _insert_default_recommendations(self, cursor):
        """Insert default warmup recommendations."""
        recommendations = [
            (1, 'phase_1', 20, 1.0, 3.0, 'Start very slow. Send to your most engaged recipients first.'),
            (2, 'phase_1', 20, 1.0, 3.0, 'Maintain low volume. Monitor bounce rates closely.'),
            (3, 'phase_1', 20, 1.0, 3.0, 'Complete first phase. Check for any delivery issues.'),
            (4, 'phase_2', 50, 1.5, 4.0, 'Increase volume slightly. Continue monitoring engagement.'),
            (5, 'phase_2', 50, 1.5, 4.0, 'Steady growth. Ensure content quality remains high.'),
            (6, 'phase_2', 50, 1.5, 4.0, 'Mid-phase check. Adjust if bounce rate exceeds 2%.'),
            (7, 'phase_2', 50, 1.5, 4.0, 'Complete second phase. Review overall performance.'),
            (8, 'phase_3', 100, 2.0, 5.0, 'Moderate increase. Segment your list for better targeting.'),
            (14, 'phase_3', 100, 2.0, 5.0, 'Maintain steady volume. Focus on engagement metrics.'),
            (15, 'phase_4', 250, 2.0, 5.0, 'Significant increase. Monitor spam folder placement.'),
            (21, 'phase_4', 250, 2.0, 5.0, 'Near full volume. Ensure list hygiene is maintained.'),
            (22, 'phase_5', 500, 1.0, 3.0, 'Full warmup complete. Maintain consistent sending patterns.'),
        ]

        for day, phase, limit, delay_min, delay_max, tips in recommendations:
            cursor.execute('''
                INSERT INTO warmup_recommendations 
                (day, phase, recommended_limit, recommended_delay_min, recommended_delay_max, tips)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (day, phase, limit, delay_min, delay_max, tips))

    def start_warmup(
        self,
        email: str,
        start_date: datetime = None,
        notes: str = None
    ) -> int:
        """
        Start a new warmup session for an email account.

        Args:
            email: Email address to warm up
            start_date: Start date (defaults to today)
            notes: Optional notes

        Returns:
            Session ID
        """
        if start_date is None:
            start_date = datetime.now()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check for existing active session
        cursor.execute('''
            SELECT id FROM warmup_sessions 
            WHERE email = ? AND status = 'active'
        ''', (email,))

        if cursor.fetchone():
            conn.close()
            raise ValueError(f"Active warmup session already exists for {email}")

        cursor.execute('''
            INSERT INTO warmup_sessions 
            (email, start_date, notes)
            VALUES (?, ?, ?)
        ''', (email, start_date.date().isoformat(), notes))

        session_id = cursor.lastrowid

        # Create initial daily log entry
        cursor.execute('''
            INSERT INTO warmup_daily_log (session_id, date, phase)
            VALUES (?, ?, 'phase_1')
        ''', (session_id, start_date.date().isoformat()))

        conn.commit()
        conn.close()

        return session_id

    def get_session(self, session_id: int) -> Optional[dict]:
        """Get warmup session details."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM warmup_sessions WHERE id = ?', (session_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return dict(row)
        return None

    def get_active_session(self, email: str) -> Optional[dict]:
        """Get active warmup session for an email."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM warmup_sessions 
            WHERE email = ? AND status = 'active'
        ''', (email,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return dict(row)
        return None

    def get_current_phase(self, session_id: int) -> WarmupPhase:
        """Get the current phase for a session."""
        session = self.get_session(session_id)
        if not session:
            return WarmupPhase.PHASE_1

        phase_code = session.get('current_phase', 'phase_1')
        for phase in WarmupPhase:
            if phase.code == phase_code:
                return phase

        return WarmupPhase.PHASE_1

    def get_recommendation_for_day(self, day: int) -> dict:
        """Get warmup recommendation for a specific day."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Find the recommendation for this day or the closest previous day
        cursor.execute('''
            SELECT * FROM warmup_recommendations 
            WHERE day <= ? 
            ORDER BY day DESC 
            LIMIT 1
        ''', (day,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return dict(row)

        # Default recommendation
        return {
            'day': day,
            'phase': 'phase_5',
            'recommended_limit': 500,
            'recommended_delay_min': 1.0,
            'recommended_delay_max': 3.0,
            'tips': 'Maintain consistent sending patterns and monitor engagement.'
        }

    def record_send(
        self,
        session_id: int,
        success: bool = True,
        delay: float = None
    ):
        """Record an email send during warmup."""
        session = self.get_session(session_id)
        if not session:
            return

        today = datetime.now().date().isoformat()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Update session stats
        if success:
            cursor.execute('''
                UPDATE warmup_sessions 
                SET total_sent = total_sent + 1 
                WHERE id = ?
            ''', (session_id,))
        else:
            cursor.execute('''
                UPDATE warmup_sessions 
                SET total_failed = total_failed + 1 
                WHERE id = ?
            ''', (session_id,))

        # Update daily log
        cursor.execute('''
            SELECT id, emails_sent, emails_failed FROM warmup_daily_log 
            WHERE session_id = ? AND date = ?
        ''', (session_id, today))

        row = cursor.fetchone()

        if row:
            log_id, sent, failed = row
            if success:
                cursor.execute('''
                    UPDATE warmup_daily_log SET emails_sent = ? WHERE id = ?
                ''', (sent + 1, log_id))
            else:
                cursor.execute('''
                    UPDATE warmup_daily_log SET emails_failed = ? WHERE id = ?
                ''', (failed + 1, log_id))

            if delay:
                cursor.execute('''
                    UPDATE warmup_daily_log 
                    SET avg_delay = COALESCE(avg_delay, 0) + ? 
                    WHERE id = ?
                ''', (delay, log_id))
        else:
            # Create new daily log entry
            cursor.execute('''
                INSERT INTO warmup_daily_log 
                (session_id, date, phase, emails_sent, emails_failed, avg_delay)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (session_id, today, session['current_phase'], 
                  1 if success else 0, 0 if success else 1, delay or 0))

        conn.commit()
        conn.close()

    def advance_day(self, session_id: int) -> bool:
        """
        Advance to the next day of warmup.

        This should be called once per day to progress through phases.
        """
        session = self.get_session(session_id)
        if not session or session['status'] != 'active':
            return False

        new_day = session['current_day'] + 1
        recommendation = self.get_recommendation_for_day(new_day)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Update session
        cursor.execute('''
            UPDATE warmup_sessions 
            SET current_day = ?, 
                current_phase = ?,
                target_daily_limit = ?
            WHERE id = ?
        ''', (new_day, recommendation['phase'], recommendation['recommended_limit'], session_id))

        # Create new daily log entry
        today = datetime.now().date().isoformat()
        cursor.execute('''
            INSERT OR IGNORE INTO warmup_daily_log 
            (session_id, date, phase)
            VALUES (?, ?, ?)
        ''', (session_id, today, recommendation['phase']))

        # Check if warmup is complete (day 28+)
        if new_day >= 28:
            cursor.execute('''
                UPDATE warmup_sessions 
                SET status = 'completed', completed_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (session_id,))

        conn.commit()
        conn.close()

        return True

    def complete_warmup(self, session_id: int) -> bool:
        """Mark a warmup session as complete."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE warmup_sessions 
            SET status = 'completed', completed_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (session_id,))

        updated = cursor.rowcount > 0
        conn.commit()
        conn.close()

        return updated

    def pause_warmup(self, session_id: int) -> bool:
        """Pause a warmup session."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE warmup_sessions 
            SET status = 'paused'
            WHERE id = ?
        ''', (session_id,))

        updated = cursor.rowcount > 0
        conn.commit()
        conn.close()

        return updated

    def resume_warmup(self, session_id: int) -> bool:
        """Resume a paused warmup session."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE warmup_sessions 
            SET status = 'active'
            WHERE id = ? AND status = 'paused'
        ''', (session_id,))

        updated = cursor.rowcount > 0
        conn.commit()
        conn.close()

        return updated

    def get_warmup_settings(self, session_id: int) -> dict:
        """
        Get current warmup settings for sending.

        Returns recommended limits and delays based on current phase.
        """
        session = self.get_session(session_id)
        if not session:
            return self._get_default_settings()

        current_day = session['current_day']
        recommendation = self.get_recommendation_for_day(current_day)
        phase = self.get_current_phase(session_id)

        # Calculate remaining sends for today
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        today = datetime.now().date().isoformat()
        cursor.execute('''
            SELECT emails_sent FROM warmup_daily_log 
            WHERE session_id = ? AND date = ?
        ''', (session_id, today))

        row = cursor.fetchone()
        sent_today = row[0] if row else 0

        conn.close()

        return {
            'session_id': session_id,
            'email': session['email'],
            'day': current_day,
            'phase': phase.code,
            'phase_description': phase.description,
            'daily_limit': recommendation['recommended_limit'],
            'sent_today': sent_today,
            'remaining_today': max(0, recommendation['recommended_limit'] - sent_today),
            'delay_min': recommendation['recommended_delay_min'],
            'delay_max': recommendation['recommended_delay_max'],
            'tips': recommendation['tips'],
            'is_complete': session['status'] == 'completed',
            'status': session['status']
        }

    def _get_default_settings(self) -> dict:
        """Get default warmup settings (no active session)."""
        return {
            'session_id': None,
            'email': None,
            'day': 0,
            'phase': 'none',
            'phase_description': 'No active warmup session',
            'daily_limit': 500,
            'sent_today': 0,
            'remaining_today': 500,
            'delay_min': 1.0,
            'delay_max': 3.0,
            'tips': 'Consider starting a warmup session for new email accounts.',
            'is_complete': True,
            'status': 'none'
        }

    def get_all_sessions(self, include_completed: bool = False) -> List[dict]:
        """Get all warmup sessions."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if include_completed:
            cursor.execute('SELECT * FROM warmup_sessions ORDER BY created_at DESC')
        else:
            cursor.execute("SELECT * FROM warmup_sessions WHERE status != 'completed' ORDER BY created_at DESC")

        sessions = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return sessions

    def get_session_history(self, session_id: int) -> List[dict]:
        """Get daily history for a warmup session."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM warmup_daily_log 
            WHERE session_id = ? 
            ORDER BY date ASC
        ''', (session_id,))

        history = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return history

    def get_statistics(self) -> dict:
        """Get overall warmup statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        stats = {}

        # Session counts
        cursor.execute('''
            SELECT status, COUNT(*) as count 
            FROM warmup_sessions 
            GROUP BY status
        ''')
        stats['sessions_by_status'] = {row[0]: row[1] for row in cursor.fetchall()}

        # Total warmup sends
        cursor.execute('SELECT SUM(total_sent) FROM warmup_sessions')
        stats['total_warmup_sends'] = cursor.fetchone()[0] or 0

        # Active sessions
        cursor.execute('SELECT COUNT(*) FROM warmup_sessions WHERE status = ?', ('active',))
        stats['active_sessions'] = cursor.fetchone()[0]

        conn.close()

        return stats


if __name__ == '__main__':
    import sys

    print("=" * 60)
    print("Warm-up Manager")
    print("=" * 60)

    manager = WarmupManager()

    if len(sys.argv) < 2:
        print("\nUsage: python warmup_manager.py <command> [args]")
        print("\nCommands:")
        print("  start <email>         - Start warmup for an email account")
        print("  status [session_id]   - Show warmup status/settings")
        print("  advance <session_id>  - Advance to next day")
        print("  complete <session_id> - Mark warmup as complete")
        print("  pause <session_id>    - Pause warmup")
        print("  resume <session_id>   - Resume paused warmup")
        print("  list                  - List all sessions")
        print("  history <session_id>  - Show session history")
        print("  stats                 - Show statistics")
        print("  phases                - Show warmup phases info")
        sys.exit(0)

    command = sys.argv[1]

    if command == 'start' and len(sys.argv) > 2:
        email = sys.argv[2]
        try:
            session_id = manager.start_warmup(email)
            print(f"\n✓ Warmup started for {email}")
            print(f"  Session ID: {session_id}")
            print(f"  Starting at: 20 emails/day with 1-3s delays")
            print(f"  Run 'status {session_id}' to see current settings")
        except ValueError as e:
            print(f"✗ Error: {e}")

    elif command == 'status':
        session_id = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        
        settings = manager.get_warmup_settings(session_id)
        
        if settings['session_id'] is None:
            print(f"\nNo active warmup session found for ID {session_id}")
        else:
            print(f"\n{'='*50}")
            print(f"Warmup Status: {settings['email']}")
            print(f"{'='*50}")
            print(f"  Session ID:    {settings['session_id']}")
            print(f"  Status:        {settings['status']}")
            print(f"  Day:           {settings['day']}")
            print(f"  Phase:         {settings['phase']} - {settings['phase_description']}")
            print(f"  Daily Limit:   {settings['daily_limit']} emails")
            print(f"  Sent Today:    {settings['sent_today']}")
            print(f"  Remaining:     {settings['remaining_today']}")
            print(f"  Delay Range:   {settings['delay_min']}s - {settings['delay_max']}s")
            print(f"\n  💡 Tip: {settings['tips']}")
            print(f"{'='*50}")

    elif command == 'advance' and len(sys.argv) > 2:
        session_id = int(sys.argv[2])
        if manager.advance_day(session_id):
            settings = manager.get_warmup_settings(session_id)
            print(f"✓ Advanced to day {settings['day']}")
            print(f"  New limit: {settings['daily_limit']} emails/day")
            print(f"  New delays: {settings['delay_min']}s - {settings['delay_max']}s")
        else:
            print(f"✗ Failed to advance session {session_id}")

    elif command == 'complete' and len(sys.argv) > 2:
        session_id = int(sys.argv[2])
        if manager.complete_warmup(session_id):
            print(f"✓ Warmup session {session_id} marked as complete")
        else:
            print(f"✗ Failed to complete session {session_id}")

    elif command == 'pause' and len(sys.argv) > 2:
        session_id = int(sys.argv[2])
        if manager.pause_warmup(session_id):
            print(f"✓ Warmup session {session_id} paused")
        else:
            print(f"✗ Failed to pause session {session_id}")

    elif command == 'resume' and len(sys.argv) > 2:
        session_id = int(sys.argv[2])
        if manager.resume_warmup(session_id):
            print(f"✓ Warmup session {session_id} resumed")
        else:
            print(f"✗ Failed to resume session {session_id}")

    elif command == 'list':
        sessions = manager.get_all_sessions(include_completed=False)
        if not sessions:
            print("\nNo active warmup sessions")
        else:
            print(f"\n{'ID':<6} {'Email':<30} {'Day':<6} {'Phase':<10} {'Status':<10} {'Sent':<8}")
            print("-" * 75)
            for s in sessions:
                print(f"{s['id']:<6} {s['email']:<30} {s['current_day']:<6} "
                      f"{s['current_phase']:<10} {s['status']:<10} {s['total_sent']:<8}")

    elif command == 'history' and len(sys.argv) > 2:
        session_id = int(sys.argv[2])
        history = manager.get_session_history(session_id)
        if not history:
            print(f"\nNo history for session {session_id}")
        else:
            print(f"\n{'Date':<12} {'Phase':<12} {'Sent':<8} {'Failed':<8} {'Avg Delay':<12}")
            print("-" * 55)
            for h in history:
                avg_delay = h.get('avg_delay', 0) / max(1, h.get('emails_sent', 1))
                print(f"{h['date']:<12} {h['phase']:<12} {h['emails_sent']:<8} "
                      f"{h['emails_failed']:<8} {avg_delay:.2f}s")

    elif command == 'stats':
        stats = manager.get_statistics()
        print(f"\nWarmup Statistics:")
        print(f"  Active Sessions: {stats.get('active_sessions', 0)}")
        print(f"  Completed: {stats.get('sessions_by_status', {}).get('completed', 0)}")
        print(f"  Paused: {stats.get('sessions_by_status', {}).get('paused', 0)}")
        print(f"  Total Warmup Sends: {stats.get('total_warmup_sends', 0):,}")

    elif command == 'phases':
        print(f"\n{'='*60}")
        print("Warm-up Phases")
        print(f"{'='*60}")
        for phase in WarmupPhase:
            print(f"\n{phase.code.upper()}")
            print(f"  Description: {phase.description}")
            print(f"  Daily Limit: {phase.daily_limit} emails")
            print(f"  Delay Range: {phase.delay_min}s - {phase.delay_max}s")
        print(f"\n{'='*60}")

    else:
        print(f"Unknown command: {command}")
        print("Run without arguments to see usage")
