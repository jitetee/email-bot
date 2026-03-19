"""Campaign Statistics Dashboard - View analytics and reports."""
import json
from pathlib import Path
from datetime import datetime
from typing import List, Optional


class StatsDashboard:
    """View and analyze campaign statistics."""
    
    def __init__(self, logs_dir: Path = None):
        if logs_dir is None:
            logs_dir = Path(__file__).parent / 'logs'
        self.logs_dir = logs_dir
        self.logs_dir.mkdir(parents=True, exist_ok=True)
    
    def get_campaign_logs(self, limit: int = 20) -> List[dict]:
        """Get recent campaign logs."""
        logs = []
        
        for log_file in sorted(self.logs_dir.glob("campaign_*.log"), reverse=True):
            if len(logs) >= limit:
                break
            
            stats = self._parse_log_file(log_file)
            if stats:
                logs.append(stats)
        
        return logs
    
    def _parse_log_file(self, log_file: Path) -> Optional[dict]:
        """Parse a campaign log file."""
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            if not lines:
                return None
            
            # Parse header
            stats = {
                'file': log_file.name,
                'path': str(log_file),
                'started': None,
                'total': 0,
                'sent': 0,
                'failed': 0,
                'duration': None,
                'delay_range': 'N/A',
                'batch_size': 'N/A'
            }
            
            for line in lines[:10]:  # Check first 10 lines for metadata
                line = line.strip()
                
                if 'Campaign started:' in line:
                    stats['started'] = line.split(':')[1].strip()
                elif 'Total emails:' in line:
                    stats['total'] = int(line.split(':')[1].strip())
                elif 'Delay range:' in line:
                    stats['delay_range'] = line.split(':')[1].strip()
                elif 'Batch size:' in line:
                    stats['batch_size'] = line.split(':')[1].strip()
            
            # Count sent/failed from log entries
            for line in lines:
                if line.startswith('[✓]') or '✓' in line:
                    stats['sent'] += 1
                elif line.startswith('[✗]') or '✗' in line:
                    stats['failed'] += 1
            
            # If no counts found, use totals
            if stats['sent'] == 0 and stats['failed'] == 0:
                stats['sent'] = stats['total']
            
            return stats
            
        except Exception as e:
            return None
    
    def get_summary(self) -> dict:
        """Get overall summary of all campaigns."""
        logs = self.get_campaign_logs(limit=100)

        if not logs:
            return {
                'total_campaigns': 0,
                'total_emails': 0,
                'total_sent': 0,
                'total_failed': 0,
                'success_rate': 0,
                'last_campaign': None,
                'avg_emails_per_campaign': 0
            }

        total_emails = sum(log.get('total', 0) for log in logs)
        total_sent = sum(log.get('sent', 0) for log in logs)
        total_failed = sum(log.get('failed', 0) for log in logs)

        return {
            'total_campaigns': len(logs),
            'total_emails': total_emails,
            'total_sent': total_sent,
            'total_failed': total_failed,
            'success_rate': (total_sent / total_emails * 100) if total_emails > 0 else 0,
            'last_campaign': logs[0]['started'] if logs else None,
            'avg_emails_per_campaign': total_emails / len(logs) if logs else 0
        }
    
    def get_recent_campaigns(self, limit: int = 10) -> List[dict]:
        """Get recent campaigns with formatted data."""
        logs = self.get_campaign_logs(limit=limit)
        
        formatted = []
        for log in logs:
            formatted.append({
                'date': log.get('started', 'Unknown')[:10] if log.get('started') else 'Unknown',
                'time': log.get('started', 'Unknown')[11:16] if log.get('started') else 'Unknown',
                'file': log.get('file', 'Unknown'),
                'total': log.get('total', 0),
                'sent': log.get('sent', 0),
                'failed': log.get('failed', 0),
                'success_rate': (log.get('sent', 0) / log.get('total', 1) * 100),
                'delay_range': log.get('delay_range', 'N/A'),
                'batch_size': log.get('batch_size', 'N/A')
            })
        
        return formatted
    
    def print_dashboard(self):
        """Print formatted dashboard to console."""
        summary = self.get_summary()
        recent = self.get_recent_campaigns(limit=5)
        
        print("\n" + "=" * 70)
        print("📊 EMAIL CAMPAIGN DASHBOARD")
        print("=" * 70)
        
        print("\n📈 OVERALL STATISTICS")
        print("-" * 70)
        print(f"  Total Campaigns:     {summary['total_campaigns']}")
        print(f"  Total Emails Sent:   {summary['total_sent']:,}")
        print(f"  Total Failed:        {summary['total_failed']:,}")
        print(f"  Overall Success Rate:{summary['success_rate']:.1f}%")
        print(f"  Avg Emails/Campaign: {summary['avg_emails_per_campaign']:.0f}")
        print(f"  Last Campaign:       {summary['last_campaign'] or 'None'}")
        
        print("\n📋 RECENT CAMPAIGNS")
        print("-" * 70)
        print(f"  {'Date':<12} {'Time':<8} {'Total':<8} {'Sent':<8} {'Failed':<8} {'Rate':<8} {'Delays'}")
        print("-" * 70)
        
        for camp in recent:
            print(f"  {camp['date']:<12} {camp['time']:<8} {camp['total']:<8} "
                  f"{camp['sent']:<8} {camp['failed']:<8} {camp['success_rate']:.1f}%    "
                  f"{camp['delay_range']}")
        
        print("-" * 70)
        
        # Performance tips
        print("\n💡 PERFORMANCE TIPS")
        print("-" * 70)
        
        if summary['success_rate'] < 90:
            print("  ⚠️  Success rate below 90% - Check email list quality")
        
        if summary['total_campaigns'] == 0:
            print("  📭 No campaigns yet - Start your first campaign!")
        elif summary['total_campaigns'] < 5:
            print("  📈 Consider A/B testing different templates")
        
        print("  ⏱️  Use random delays (2-5s) to avoid spam filters")
        print("  📦 Keep batch sizes under 25 for better deliverability")
        print("  🧹 Clean your email list regularly")
        
        print("\n" + "=" * 70 + "\n")
    
    def export_report(self, output_file: Path = None) -> Path:
        """Export campaign report to JSON."""
        if output_file is None:
            output_file = self.logs_dir / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'summary': self.get_summary(),
            'recent_campaigns': self.get_recent_campaigns(limit=50),
            'top_performers': [],  # Would need more data to calculate
            'recommendations': []
        }
        
        # Add recommendations
        summary = report['summary']
        if summary['success_rate'] < 95:
            report['recommendations'].append("Clean email list to improve success rate")
        if summary['total_campaigns'] > 0:
            report['recommendations'].append("Consider A/B testing for better results")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        return output_file


if __name__ == '__main__':
    dashboard = StatsDashboard()
    dashboard.print_dashboard()
    
    # Export report
    if input("\nExport detailed report? (y/n): ").lower() == 'y':
        report_path = dashboard.export_report()
        print(f"Report exported to: {report_path}")
