"""Batch Email Processor - Process emails in batches with retry logic."""
import json
import time
from pathlib import Path
from typing import Dict, List, Callable
from datetime import datetime


class BatchProcessor:
    """Process email lists in batches with retry and error handling."""

    def __init__(self, batch_size: int = 50, retry_count: int = 3,
                 delay_between_batches: int = 30):
        self.batch_size = batch_size
        self.retry_count = retry_count
        self.delay_between_batches = delay_between_batches
        self.log_file = Path(__file__).parent / 'logs' / 'batch_processor.log'
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def log(self, message: str):
        """Log message to file and console."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}\n"
        
        # Console output
        print(log_entry.strip())
        
        # File log
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)

    def split_into_batches(self, items: List, batch_size: int = None) -> List[List]:
        """Split list into batches."""
        batch_size = batch_size or self.batch_size
        return [items[i:i + batch_size] for i in range(0, len(items), batch_size)]

    def process_batch(self, batch: List, processor_func: Callable, 
                     batch_num: int, total_batches: int) -> Dict:
        """
        Process a single batch with retry logic.
        
        Args:
            batch: List of items to process
            processor_func: Function to process each item
            batch_num: Current batch number
            total_batches: Total number of batches
        
        Returns:
            Dict with batch results
        """
        self.log(f"Processing batch {batch_num}/{total_batches} ({len(batch)} items)")
        
        results = {
            'batch_num': batch_num,
            'total': len(batch),
            'success': 0,
            'failed': 0,
            'retried': 0,
            'errors': []
        }

        for i, item in enumerate(batch, 1):
            success = False
            attempts = 0
            
            while not success and attempts < self.retry_count:
                try:
                    attempts += 1
                    result = processor_func(item)
                    
                    if result:
                        results['success'] += 1
                        success = True
                        
                        # Progress indicator
                        if i % 10 == 0:
                            self.log(f"  Progress: {i}/{len(batch)}")
                    else:
                        raise Exception("Processor returned False")
                        
                except Exception as e:
                    if attempts >= self.retry_count:
                        results['failed'] += 1
                        results['errors'].append({
                            'item': str(item)[:50],
                            'error': str(e),
                            'attempts': attempts
                        })
                        self.log(f"  ✗ Failed after {attempts} attempts: {str(e)[:50]}")
                    else:
                        results['retried'] += 1
                        self.log(f"  ⚠ Retry {attempts}/{self.retry_count} for item {i}")
                        time.sleep(2)  # Wait before retry

        return results

    def process_list(self, items: List, processor_func: Callable, 
                    description: str = "items") -> Dict:
        """
        Process entire list in batches.
        
        Args:
            items: List of items to process
            processor_func: Function to process each item
            description: Description of items being processed
        
        Returns:
            Dict with overall results
        """
        start_time = datetime.now()
        self.log(f"Starting batch processing: {len(items)} {description}")
        self.log(f"Batch size: {self.batch_size}, Retries: {self.retry_count}")
        
        batches = self.split_into_batches(items)
        total_batches = len(batches)
        
        overall_results = {
            'description': description,
            'total_items': len(items),
            'total_batches': total_batches,
            'batches_processed': 0,
            'total_success': 0,
            'total_failed': 0,
            'total_retried': 0,
            'all_errors': [],
            'start_time': start_time.isoformat(),
            'end_time': None,
            'duration_seconds': None
        }

        for i, batch in enumerate(batches, 1):
            # Process batch
            batch_results = self.process_batch(batch, processor_func, i, total_batches)
            
            # Aggregate results
            overall_results['batches_processed'] += 1
            overall_results['total_success'] += batch_results['success']
            overall_results['total_failed'] += batch_results['failed']
            overall_results['total_retried'] += batch_results['retried']
            overall_results['all_errors'].extend(batch_results['errors'])

            # Delay between batches (except for last batch)
            if i < total_batches:
                self.log(f"Waiting {self.delay_between_batches}s before next batch...")
                time.sleep(self.delay_between_batches)

        # Calculate duration
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        overall_results['end_time'] = end_time.isoformat()
        overall_results['duration_seconds'] = duration

        # Summary
        self.log("=" * 60)
        self.log("Batch Processing Complete!")
        self.log(f"Total: {overall_results['total_items']}")
        self.log(f"Success: {overall_results['total_success']}")
        self.log(f"Failed: {overall_results['total_failed']}")
        self.log(f"Retried: {overall_results['total_retried']}")
        self.log(f"Duration: {duration:.2f}s")
        self.log(f"Speed: {overall_results['total_items']/duration:.2f} items/second")
        self.log("=" * 60)

        return overall_results

    def save_results(self, results: Dict, output_file: Path = None):
        """Save processing results to JSON file."""
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = Path(__file__).parent / 'logs' / f'batch_results_{timestamp}.json'
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str)
        
        self.log(f"Results saved to: {output_file}")
        return output_file

    def get_statistics(self) -> Dict:
        """Get statistics from log file."""
        if not self.log_file.exists():
            return {'error': 'No log file found'}
        
        stats = {
            'total_runs': 0,
            'total_items_processed': 0,
            'total_success': 0,
            'total_failed': 0,
            'last_run': None
        }
        
        with open(self.log_file, 'r', encoding='utf-8') as f:
            for line in f:
                if 'Starting batch processing' in line:
                    stats['total_runs'] += 1
                if 'Total:' in line:
                    try:
                        count = int(line.split(':')[1].strip())
                        stats['total_items_processed'] += count
                    except:
                        pass
                if 'Success:' in line:
                    try:
                        count = int(line.split(':')[1].strip())
                        stats['total_success'] += count
                    except:
                        pass
                if 'Failed:' in line:
                    try:
                        count = int(line.split(':')[1].strip())
                        stats['total_failed'] += count
                    except:
                        pass
        
        return stats


# Example processor functions
def example_email_processor(email: str) -> bool:
    """Example: Process email (e.g., validate, send, etc.)."""
    # Simulate processing
    if '@' in email and '.' in email:
        return True
    return False


if __name__ == '__main__':
    import sys

    processor = BatchProcessor(batch_size=50, retry_count=3, delay_between_batches=10)

    print("=" * 60)
    print("Batch Email Processor")
    print("=" * 60)

    if len(sys.argv) < 2:
        print("\nUsage: python batch_processor.py <command> [args]")
        print("\nCommands:")
        print("  demo                    - Run demo processing")
        print("  process <file>          - Process email list from file")
        print("  stats                   - Show processing statistics")
        print("  test <count>            - Test with N items")
        sys.exit(0)

    command = sys.argv[1]

    if command == 'demo':
        # Demo with sample emails
        test_emails = [
            f"user{i}@example.com" for i in range(1, 101)
        ]
        
        results = processor.process_list(test_emails, example_email_processor, "demo emails")
        processor.save_results(results)

    elif command == 'process':
        if len(sys.argv) < 3:
            print("Usage: python batch_processor.py process <email_list.txt>")
            sys.exit(1)
        
        # Load email list
        email_file = Path(sys.argv[2])
        if not email_file.exists():
            print(f"File not found: {email_file}")
            sys.exit(1)
        
        emails = []
        with open(email_file, 'r', encoding='utf-8') as f:
            for line in f:
                email = line.strip()
                if email and not email.startswith('#') and '@' in email:
                    emails.append(email)
        
        print(f"Loaded {len(emails)} emails from {email_file}")
        
        # Process
        results = processor.process_list(emails, example_email_processor, "emails")
        processor.save_results(results)

    elif command == 'stats':
        stats = processor.get_statistics()
        print("\nBatch Processor Statistics:")
        print("=" * 60)
        print(f"Total Runs: {stats.get('total_runs', 0)}")
        print(f"Total Items Processed: {stats.get('total_items_processed', 0)}")
        print(f"Total Success: {stats.get('total_success', 0)}")
        print(f"Total Failed: {stats.get('total_failed', 0)}")
        print("=" * 60)

    elif command == 'test':
        count = int(sys.argv[2]) if len(sys.argv) > 2 else 100
        test_items = [f"item{i}@test.com" for i in range(1, count + 1)]
        
        print(f"Testing with {count} items...")
        results = processor.process_list(test_items, example_email_processor, "test items")
        print(f"\nTest completed in {results['duration_seconds']:.2f} seconds")

    else:
        print(f"Unknown command: {command}")
