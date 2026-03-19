"""A/B Testing - Test multiple templates and subjects to optimize performance."""
import sqlite3
import random
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Tuple
from enum import Enum
from dataclasses import dataclass


class TestStatus(Enum):
    DRAFT = "draft"
    RUNNING = "running"
    COMPLETED = "completed"
    STOPPED = "stopped"


class WinnerCriterion(Enum):
    OPEN_RATE = "open_rate"
    CLICK_RATE = "click_rate"
    CONVERSION_RATE = "conversion_rate"
    LOWEST_BOUNCE = "lowest_bounce"


@dataclass
class TestVariant:
    """A variant in an A/B test."""
    id: int
    name: str
    template: str
    subject: str
    test_id: int
    emails_sent: int = 0
    opens: int = 0
    clicks: int = 0
    bounces: int = 0
    unsubscribes: int = 0


class ABTestManager:
    """Manage A/B tests for email campaigns."""

    def __init__(self, db_path: Path = None, tracking_db: Path = None):
        if db_path is None:
            db_path = Path(__file__).parent / 'data' / 'ab_tests.db'
        
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        
        # Optional tracking integration
        self.tracking_db = tracking_db

    def _init_db(self):
        """Initialize the A/B test database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # A/B tests table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ab_tests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'draft',
                email_list_file TEXT NOT NULL,
                sample_size_percent REAL DEFAULT 20,
                winner_criterion TEXT DEFAULT 'open_rate',
                confidence_threshold REAL DEFAULT 95,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                winner_variant_id INTEGER,
                total_emails INTEGER DEFAULT 0,
                sender_email TEXT,
                sender_name TEXT,
                smtp_account_id INTEGER,
                batch_size INTEGER DEFAULT 25,
                delay_min REAL DEFAULT 1.0,
                delay_max REAL DEFAULT 3.0,
                notes TEXT
            )
        ''')

        # Test variants table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_variants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                template TEXT NOT NULL,
                subject TEXT NOT NULL,
                emails_sent INTEGER DEFAULT 0,
                opens INTEGER DEFAULT 0,
                clicks INTEGER DEFAULT 0,
                bounces INTEGER DEFAULT 0,
                unsubscribes INTEGER DEFAULT 0,
                is_winner INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (test_id) REFERENCES ab_tests(id)
            )
        ''');

        # Test assignments (which email gets which variant)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_id INTEGER NOT NULL,
                email TEXT NOT NULL,
                variant_id INTEGER NOT NULL,
                sent_at TIMESTAMP,
                opened_at TIMESTAMP,
                clicked_at TIMESTAMP,
                bounced INTEGER DEFAULT 0,
                unsubscribed INTEGER DEFAULT 0,
                FOREIGN KEY (test_id) REFERENCES ab_tests(id),
                FOREIGN KEY (variant_id) REFERENCES test_variants(id)
            )
        ''');

        # Test results log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_id INTEGER,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                variant_id INTEGER,
                metric_type TEXT,
                metric_value REAL,
                sample_size INTEGER,
                FOREIGN KEY (test_id) REFERENCES ab_tests(id),
                FOREIGN KEY (variant_id) REFERENCES test_variants(id)
            )
        ''');

        conn.commit()
        conn.close()

    def create_test(
        self,
        name: str,
        email_list_file: str,
        variants: List[Dict],
        description: str = None,
        sample_size_percent: float = 20,
        winner_criterion: str = "open_rate",
        confidence_threshold: float = 95,
        sender_email: str = None,
        sender_name: str = None,
        batch_size: int = 25,
        delay_min: float = 1.0,
        delay_max: float = 3.0,
        notes: str = None
    ) -> int:
        """
        Create a new A/B test.

        Args:
            name: Test name
            email_list_file: Path to email list
            variants: List of variant dicts with 'name', 'template', 'subject'
            description: Test description
            sample_size_percent: Percent of list to use for test (rest gets winner)
            winner_criterion: How to determine winner (open_rate, click_rate, etc.)
            confidence_threshold: Statistical confidence threshold
            sender_email: Sender email address
            sender_name: Sender name
            batch_size: Emails per batch
            delay_min: Minimum delay between emails
            delay_max: Maximum delay between emails
            notes: Additional notes

        Returns:
            Test ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create test
        cursor.execute('''
            INSERT INTO ab_tests (
                name, description, email_list_file, sample_size_percent,
                winner_criterion, confidence_threshold, sender_email, sender_name,
                batch_size, delay_min, delay_max, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, description, email_list_file, sample_size_percent,
              winner_criterion, confidence_threshold, sender_email, sender_name,
              batch_size, delay_min, delay_max, notes))

        test_id = cursor.lastrowid

        # Create variants
        for variant in variants:
            cursor.execute('''
                INSERT INTO test_variants (test_id, name, template, subject)
                VALUES (?, ?, ?, ?)
            ''', (test_id, variant['name'], variant['template'], variant['subject']))

        conn.commit()
        conn.close()

        return test_id

    def add_variant(
        self,
        test_id: int,
        name: str,
        template: str,
        subject: str
    ) -> int:
        """Add a variant to an existing test."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO test_variants (test_id, name, template, subject)
            VALUES (?, ?, ?, ?)
        ''', (test_id, name, template, subject))

        variant_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return variant_id

    def get_test(self, test_id: int) -> Optional[dict]:
        """Get test details."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM ab_tests WHERE id = ?', (test_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return dict(row)
        return None

    def get_variants(self, test_id: int) -> List[TestVariant]:
        """Get all variants for a test."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM test_variants WHERE test_id = ? ORDER BY id
        ''', (test_id,))

        variants = [TestVariant(**dict(row)) for row in cursor.fetchall()]
        conn.close()

        return variants

    def start_test(self, test_id: int) -> bool:
        """Start an A/B test."""
        test = self.get_test(test_id)
        if not test:
            return False

        variants = self.get_variants(test_id)
        if len(variants) < 2:
            raise ValueError("A/B test requires at least 2 variants")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Update test status
        cursor.execute('''
            UPDATE ab_tests SET status = ?, started_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (TestStatus.RUNNING.value, test_id))

        conn.commit()
        conn.close()

        return True

    def get_variant_for_email(self, test_id: int, email: str) -> Tuple[int, TestVariant]:
        """
        Get the variant assignment for an email.
        
        Uses consistent hashing to ensure same email always gets same variant.
        
        Returns:
            Tuple of (assignment_id, variant)
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Check if already assigned
        cursor.execute('''
            SELECT a.*, v.* FROM test_assignments a
            JOIN test_variants v ON a.variant_id = v.id
            WHERE a.test_id = ? AND a.email = ?
        ''', (test_id, email))

        row = cursor.fetchone()
        if row:
            conn.close()
            return row['id'], TestVariant(**dict(row))

        # Get variants and assign randomly (weighted equally)
        variants = self.get_variants(test_id)
        if not variants:
            conn.close()
            raise ValueError("No variants found for test")

        # Consistent random assignment based on email hash
        email_hash = hash(email) % len(variants)
        variant = variants[email_hash]

        # Create assignment
        cursor.execute('''
            INSERT INTO test_assignments (test_id, email, variant_id)
            VALUES (?, ?, ?)
        ''', (test_id, email, variant.id))

        assignment_id = cursor.lastrowid

        # Update variant sent count
        cursor.execute('''
            UPDATE test_variants SET emails_sent = emails_sent + 1
            WHERE id = ?
        ''', (variant.id,))

        # Update test total
        cursor.execute('''
            UPDATE ab_tests SET total_emails = total_emails + 1
            WHERE id = ?
        ''', (test_id,))

        conn.commit()
        conn.close()

        return assignment_id, variant

    def record_open(self, assignment_id: int):
        """Record an open for a test assignment."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE test_assignments SET opened_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (assignment_id,))

        # Get variant and update stats
        cursor.execute('''
            SELECT variant_id FROM test_assignments WHERE id = ?
        ''', (assignment_id,))
        row = cursor.fetchone()

        if row:
            cursor.execute('''
                UPDATE test_variants SET opens = opens + 1
                WHERE id = ?
            ''', (row[0],))

        conn.commit()
        conn.close()

    def record_click(self, assignment_id: int):
        """Record a click for a test assignment."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE test_assignments SET clicked_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (assignment_id,))

        # Get variant and update stats
        cursor.execute('''
            SELECT variant_id FROM test_assignments WHERE id = ?
        ''', (assignment_id,))
        row = cursor.fetchone()

        if row:
            cursor.execute('''
                UPDATE test_variants SET clicks = clicks + 1
                WHERE id = ?
            ''', (row[0],))

        conn.commit()
        conn.close()

    def record_bounce(self, assignment_id: int):
        """Record a bounce for a test assignment."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE test_assignments SET bounced = 1
            WHERE id = ?
        ''', (assignment_id,))

        # Get variant and update stats
        cursor.execute('''
            SELECT variant_id FROM test_assignments WHERE id = ?
        ''', (assignment_id,))
        row = cursor.fetchone()

        if row:
            cursor.execute('''
                UPDATE test_variants SET bounces = bounces + 1
                WHERE id = ?
            ''', (row[0],))

        conn.commit()
        conn.close()

    def record_unsubscribe(self, assignment_id: int):
        """Record an unsubscribe for a test assignment."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE test_assignments SET unsubscribed = 1
            WHERE id = ?
        ''', (assignment_id,))

        # Get variant and update stats
        cursor.execute('''
            SELECT variant_id FROM test_assignments WHERE id = ?
        ''', (assignment_id,))
        row = cursor.fetchone()

        if row:
            cursor.execute('''
                UPDATE test_variants SET unsubscribes = unsubscribes + 1
                WHERE id = ?
            ''', (row[0],))

        conn.commit()
        conn.close()

    def get_test_results(self, test_id: int) -> dict:
        """Get comprehensive test results."""
        test = self.get_test(test_id)
        if not test:
            return {'error': 'Test not found'}

        variants = self.get_variants(test_id)

        results = {
            'test': test,
            'variants': [],
            'winner': None,
            'statistical_significance': None
        }

        for variant in variants:
            open_rate = (variant.opens / variant.emails_sent * 100) if variant.emails_sent > 0 else 0
            click_rate = (variant.clicks / variant.emails_sent * 100) if variant.emails_sent > 0 else 0
            bounce_rate = (variant.bounces / variant.emails_sent * 100) if variant.emails_sent > 0 else 0

            results['variants'].append({
                'id': variant.id,
                'name': variant.name,
                'template': variant.template,
                'subject': variant.subject,
                'emails_sent': variant.emails_sent,
                'opens': variant.opens,
                'clicks': variant.clicks,
                'bounces': variant.bounces,
                'open_rate': open_rate,
                'click_rate': click_rate,
                'bounce_rate': bounce_rate,
                'is_winner': bool(variant.is_winner)
            })

        # Determine winner
        if test['status'] == TestStatus.COMPLETED.value and test['winner_variant_id']:
            for v in results['variants']:
                if v['id'] == test['winner_variant_id']:
                    results['winner'] = v
                    break

        return results

    def calculate_winner(self, test_id: int) -> Optional[int]:
        """
        Calculate the winning variant based on the test criterion.
        
        Returns:
            Winning variant ID or None if test is incomplete
        """
        test = self.get_test(test_id)
        if not test:
            return None

        variants = self.get_variants(test_id)
        if len(variants) < 2:
            return None

        criterion = test['winner_criterion']

        # Calculate metrics for each variant
        variant_metrics = []
        for variant in variants:
            if variant.emails_sent == 0:
                continue

            metrics = {
                'id': variant.id,
                'open_rate': variant.opens / variant.emails_sent,
                'click_rate': variant.clicks / variant.emails_sent,
                'bounce_rate': variant.bounces / variant.emails_sent,
            }
            variant_metrics.append(metrics)

        if not variant_metrics:
            return None

        # Find winner based on criterion
        if criterion == 'open_rate':
            winner = max(variant_metrics, key=lambda x: x['open_rate'])
        elif criterion == 'click_rate':
            winner = max(variant_metrics, key=lambda x: x['click_rate'])
        elif criterion == 'lowest_bounce':
            winner = min(variant_metrics, key=lambda x: x['bounce_rate'])
        else:
            winner = max(variant_metrics, key=lambda x: x['open_rate'])

        # Mark as winner
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE ab_tests SET winner_variant_id = ?, status = ?, completed_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (winner['id'], TestStatus.COMPLETED.value, test_id))

        cursor.execute('''
            UPDATE test_variants SET is_winner = 1 WHERE id = ?
        ''', (winner['id'],))

        conn.commit()
        conn.close()

        return winner['id']

    def stop_test(self, test_id: int) -> bool:
        """Stop a running test."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE ab_tests SET status = ?, completed_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (TestStatus.STOPPED.value, test_id))

        updated = cursor.rowcount > 0
        conn.commit()
        conn.close()

        return updated

    def get_all_tests(self, status: str = None) -> List[dict]:
        """Get all tests, optionally filtered by status."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if status:
            cursor.execute('SELECT * FROM ab_tests WHERE status = ? ORDER BY created_at DESC', (status,))
        else:
            cursor.execute('SELECT * FROM ab_tests ORDER BY created_at DESC')

        tests = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return tests

    def get_statistics(self) -> dict:
        """Get overall A/B test statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        stats = {}

        # Test counts by status
        cursor.execute('''
            SELECT status, COUNT(*) as count FROM ab_tests GROUP BY status
        ''')
        stats['tests_by_status'] = {row[0]: row[1] for row in cursor.fetchall()}

        # Total tests
        cursor.execute('SELECT COUNT(*) FROM ab_tests')
        stats['total_tests'] = cursor.fetchone()[0]

        # Completed tests with winners
        cursor.execute('SELECT COUNT(*) FROM ab_tests WHERE status = ? AND winner_variant_id IS NOT NULL', 
                      (TestStatus.COMPLETED.value,))
        stats['completed_with_winner'] = cursor.fetchone()[0]

        conn.close()

        return stats

    def export_results(self, test_id: int, output_file: Path) -> Path:
        """Export test results to JSON."""
        import json

        results = self.get_test_results(test_id)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str)

        return output_file


if __name__ == '__main__':
    import sys

    print("=" * 60)
    print("A/B Test Manager")
    print("=" * 60)

    manager = ABTestManager()

    if len(sys.argv) < 2:
        print("\nUsage: python ab_test_manager.py <command> [args]")
        print("\nCommands:")
        print("  create                - Create a new A/B test (interactive)")
        print("  list                  - List all tests")
        print("  start <id>            - Start a test")
        print("  stop <id>             - Stop a test")
        print("  results <id>          - View test results")
        print("  winner <id>           - Calculate and declare winner")
        print("  assign <id> <email>   - Get variant for an email")
        print("  stats                 - Show statistics")
        print("  demo                  - Create demo test")
        sys.exit(0)

    command = sys.argv[1]

    if command == 'demo':
        # Create demo A/B test
        test_id = manager.create_test(
            name="Subject Line Test",
            description="Testing different subject lines for engagement",
            email_list_file="data/email_list.txt",
            variants=[
                {'name': 'Variant A', 'template': 'modern_promo', 'subject': '🔥 Flash Sale - 50% Off Everything!'},
                {'name': 'Variant B', 'template': 'modern_promo', 'subject': 'Your Exclusive Discount Inside'},
                {'name': 'Variant C', 'template': 'modern_promo', 'subject': 'Last Chance: Big Savings End Soon'},
            ],
            sample_size_percent=20,
            winner_criterion='open_rate'
        )
        print(f"\n✓ Demo A/B test created!")
        print(f"  Test ID: {test_id}")
        print(f"  Variants: 3")
        print(f"  Run 'start {test_id}' to begin the test")

    elif command == 'list':
        tests = manager.get_all_tests()
        if not tests:
            print("\nNo A/B tests found")
        else:
            print(f"\n{'ID':<6} {'Name':<25} {'Status':<12} {'Variants':<10} {'Total Emails':<15}")
            print("-" * 70)
            for t in tests:
                variants = manager.get_variants(t['id'])
                print(f"{t['id']:<6} {t['name']:<25} {t['status']:<12} "
                      f"{len(variants):<10} {t['total_emails']:<15}")

    elif command == 'start' and len(sys.argv) > 2:
        test_id = int(sys.argv[2])
        try:
            if manager.start_test(test_id):
                print(f"✓ Test {test_id} started!")
                print("  Use 'assign <id> <email>' to get variant assignments")
            else:
                print(f"✗ Failed to start test {test_id}")
        except ValueError as e:
            print(f"✗ Error: {e}")

    elif command == 'stop' and len(sys.argv) > 2:
        test_id = int(sys.argv[2])
        if manager.stop_test(test_id):
            print(f"✓ Test {test_id} stopped")
        else:
            print(f"✗ Failed to stop test {test_id}")

    elif command == 'results' and len(sys.argv) > 2:
        test_id = int(sys.argv[2])
        results = manager.get_test_results(test_id)

        if 'error' in results:
            print(f"\n✗ {results['error']}")
        else:
            print(f"\n{'='*60}")
            print(f"A/B Test Results: {results['test']['name']}")
            print(f"{'='*60}")
            print(f"Status: {results['test']['status']}")
            print(f"Total Emails: {results['test']['total_emails']}")
            print(f"\n{'Variant':<15} {'Sent':<8} {'Opens':<8} {'Open Rate':<12} {'Clicks':<8} {'Click Rate':<12}")
            print("-" * 70)

            for v in results['variants']:
                winner_marker = " 🏆 WINNER" if v['is_winner'] else ""
                print(f"{v['name']:<15} {v['emails_sent']:<8} {v['opens']:<8} "
                      f"{v['open_rate']:.1f}%{'':<7} {v['clicks']:<8} {v['click_rate']:.1f}%{'':<7}{winner_marker}")

            if results['winner']:
                print(f"\n🏆 Winner: {results['winner']['name']}")
                print(f"   Subject: {results['winner']['subject']}")
            print(f"{'='*60}")

    elif command == 'winner' and len(sys.argv) > 2:
        test_id = int(sys.argv[2])
        winner_id = manager.calculate_winner(test_id)
        if winner_id:
            variants = manager.get_variants(test_id)
            winner = next((v for v in variants if v.id == winner_id), None)
            if winner:
                print(f"🏆 Winner declared: {winner.name}")
                print(f"   Subject: {winner.subject}")
        else:
            print("✗ Could not calculate winner (insufficient data)")

    elif command == 'assign' and len(sys.argv) > 3:
        test_id = int(sys.argv[2])
        email = sys.argv[3]
        try:
            assignment_id, variant = manager.get_variant_for_email(test_id, email)
            print(f"\nEmail: {email}")
            print(f"Assigned to: {variant.name}")
            print(f"Template: {variant.template}")
            print(f"Subject: {variant.subject}")
        except ValueError as e:
            print(f"✗ Error: {e}")

    elif command == 'stats':
        stats = manager.get_statistics()
        print(f"\nA/B Test Statistics:")
        print(f"  Total Tests: {stats.get('total_tests', 0)}")
        print(f"  By Status: {stats.get('tests_by_status', {})}")
        print(f"  Completed with Winner: {stats.get('completed_with_winner', 0)}")

    else:
        print(f"Unknown command: {command}")
        print("Run without arguments to see usage")
