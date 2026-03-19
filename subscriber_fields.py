"""Subscriber Custom Fields Manager - Add metadata to subscribers."""
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class SubscriberFieldsManager:
    """Manage custom fields for email subscribers."""

    def __init__(self, data_file: Path = None):
        self.data_file = data_file or Path(__file__).parent / 'data' / 'subscribers.json'
        self.field_definitions_file = Path(__file__).parent / 'data' / 'field_definitions.json'
        self._ensure_files_exist()

    def _ensure_files_exist(self):
        """Create data files if they don't exist."""
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        
        if not self.data_file.exists():
            self._save_data([], self.data_file)
        if not self.field_definitions_file.exists():
            self._save_default_fields()

    def _save_default_fields(self):
        """Save default field definitions."""
        defaults = {
            'fields': [
                {'name': 'first_name', 'type': 'text', 'required': False, 'label': 'First Name'},
                {'name': 'last_name', 'type': 'text', 'required': False, 'label': 'Last Name'},
                {'name': 'company', 'type': 'text', 'required': False, 'label': 'Company'},
                {'name': 'birthday', 'type': 'date', 'required': False, 'label': 'Birthday'},
                {'name': 'location', 'type': 'text', 'required': False, 'label': 'Location'},
            ]
        }
        self._save_data(defaults, self.field_definitions_file)

    def _load_data(self, file: Path):
        """Load data from JSON file."""
        try:
            with open(file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return [] if file == self.data_file else {'fields': []}

    def _save_data(self, data, file: Path):
        """Save data to JSON file."""
        with open(file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)

    def add_field_definition(self, name: str, field_type: str = 'text', 
                            required: bool = False, label: str = None) -> Dict:
        """Add a custom field definition."""
        data = self._load_data(self.field_definitions_file)
        
        # Check if field exists
        for field in data['fields']:
            if field['name'] == name:
                return {'error': f'Field "{name}" already exists'}

        field = {
            'name': name,
            'type': field_type,
            'required': required,
            'label': label or name.replace('_', ' ').title(),
            'created_at': datetime.now().isoformat()
        }

        data['fields'].append(field)
        self._save_data(data, self.field_definitions_file)
        return field

    def remove_field_definition(self, name: str) -> bool:
        """Remove a field definition."""
        data = self._load_data(self.field_definitions_file)
        original_count = len(data['fields'])
        data['fields'] = [f for f in data['fields'] if f['name'] != name]
        
        if len(data['fields']) < original_count:
            self._save_data(data, self.field_definitions_file)
            return True
        return False

    def get_field_definitions(self) -> List[Dict]:
        """Get all field definitions."""
        data = self._load_data(self.field_definitions_file)
        return data['fields']

    def add_subscriber(self, email: str, fields: Dict = None) -> Dict:
        """Add a subscriber with custom fields."""
        subscribers = self._load_data(self.data_file)
        
        # Check if subscriber exists
        for sub in subscribers:
            if sub['email'] == email:
                return {'error': f'Subscriber "{email}" already exists'}

        # Get field definitions
        field_defs = self.get_field_definitions()
        
        # Validate and set fields
        subscriber_fields = {'email': email}
        for field in field_defs:
            value = fields.get(field['name']) if fields else None
            
            # Set default value
            if field['required'] and not value:
                return {'error': f'Required field missing: {field["name"]}'}
            
            subscriber_fields[field['name']] = value

        subscriber_fields['subscribed_at'] = datetime.now().isoformat()
        subscriber_fields['tags'] = []

        subscribers.append(subscriber_fields)
        self._save_data(subscribers, self.data_file)
        return subscriber_fields

    def update_subscriber(self, email: str, fields: Dict) -> Optional[Dict]:
        """Update subscriber fields."""
        subscribers = self._load_data(self.data_file)
        
        for sub in subscribers:
            if sub['email'] == email:
                sub.update(fields)
                sub['updated_at'] = datetime.now().isoformat()
                self._save_data(subscribers, self.data_file)
                return sub
        return None

    def get_subscriber(self, email: str) -> Optional[Dict]:
        """Get subscriber by email."""
        subscribers = self._load_data(self.data_file)
        for sub in subscribers:
            if sub['email'] == email:
                return sub
        return None

    def search_subscribers(self, field: str, value: str) -> List[Dict]:
        """Search subscribers by field value."""
        subscribers = self._load_data(self.data_file)
        results = []
        
        for sub in subscribers:
            if str(sub.get(field, '')).lower() == value.lower():
                results.append(sub)
        
        return results

    def filter_subscribers(self, filters: Dict) -> List[Dict]:
        """Filter subscribers by multiple criteria."""
        subscribers = self._load_data(self.data_file)
        results = []
        
        for sub in subscribers:
            match = True
            for field, value in filters.items():
                if str(sub.get(field, '')).lower() != str(value).lower():
                    match = False
                    break
            if match:
                results.append(sub)
        
        return results

    def add_tag(self, email: str, tag: str) -> bool:
        """Add a tag to subscriber."""
        sub = self.get_subscriber(email)
        if not sub:
            return False
        
        if 'tags' not in sub:
            sub['tags'] = []
        
        if tag not in sub['tags']:
            sub['tags'].append(tag)
            self.update_subscriber(email, {'tags': sub['tags']})
        
        return True

    def remove_tag(self, email: str, tag: str) -> bool:
        """Remove a tag from subscriber."""
        sub = self.get_subscriber(email)
        if not sub or 'tags' not in sub:
            return False
        
        if tag in sub['tags']:
            sub['tags'].remove(tag)
            self.update_subscriber(email, {'tags': sub['tags']})
            return True
        return False

    def get_all_tags(self) -> List[str]:
        """Get all unique tags."""
        subscribers = self._load_data(self.data_file)
        tags = set()
        
        for sub in subscribers:
            for tag in sub.get('tags', []):
                tags.add(tag)
        
        return sorted(list(tags))

    def list_subscribers(self, limit: int = None) -> List[Dict]:
        """List all subscribers."""
        subscribers = self._load_data(self.data_file)
        if limit:
            return subscribers[:limit]
        return subscribers

    def get_statistics(self) -> Dict:
        """Get subscriber statistics."""
        subscribers = self._load_data(self.data_file)
        
        stats = {
            'total': len(subscribers),
            'with_fields': 0,
            'tags_count': 0,
            'recent_signups_7d': 0,
            'recent_signups_30d': 0,
            'field_values': {}
        }
        
        now = datetime.now()
        all_tags = set()
        
        for sub in subscribers:
            # Count subscribers with custom fields
            if len(sub) > 3:  # More than just email, subscribed_at, tags
                stats['with_fields'] += 1
            
            # Collect tags
            for tag in sub.get('tags', []):
                all_tags.add(tag)
            
            # Count recent signups
            try:
                subscribed_at = datetime.fromisoformat(sub['subscribed_at'])
                days_ago = (now - subscribed_at).days
                if days_ago <= 7:
                    stats['recent_signups_7d'] += 1
                if days_ago <= 30:
                    stats['recent_signups_30d'] += 1
            except:
                pass
            
            # Collect field value statistics
            for field, value in sub.items():
                if field not in ['email', 'subscribed_at', 'updated_at', 'tags']:
                    if field not in stats['field_values']:
                        stats['field_values'][field] = {}
                    value_str = str(value) if value else '(empty)'
                    stats['field_values'][field][value_str] = stats['field_values'][field].get(value_str, 0) + 1
        
        stats['tags_count'] = len(all_tags)
        return stats

    def export_subscribers(self, output_file: Path, fields: List[str] = None) -> int:
        """Export subscribers to CSV."""
        import csv
        
        subscribers = self._load_data(self.data_file)
        
        if not fields:
            field_defs = self.get_field_definitions()
            fields = ['email'] + [f['name'] for f in field_defs] + ['tags', 'subscribed_at']
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
            writer.writeheader()
            
            for sub in subscribers:
                # Convert tags list to string
                row = sub.copy()
                if 'tags' in row and isinstance(row['tags'], list):
                    row['tags'] = '|'.join(row['tags'])
                writer.writerow(row)
        
        return len(subscribers)

    def import_subscribers(self, input_file: Path) -> int:
        """Import subscribers from CSV."""
        import csv
        
        if not input_file.exists():
            raise FileNotFoundError(f"File not found: {input_file}")
        
        imported = 0
        with open(input_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                email = row.get('email')
                if email:
                    # Remove email from fields dict
                    fields = {k: v for k, v in row.items() if k != 'email'}
                    
                    # Convert tags string to list
                    if 'tags' in fields and fields['tags']:
                        fields['tags'] = fields['tags'].split('|')
                    
                    result = self.add_subscriber(email, fields)
                    if 'error' not in result:
                        imported += 1
        
        return imported


if __name__ == '__main__':
    import sys

    manager = SubscriberFieldsManager()

    print("=" * 60)
    print("Subscriber Custom Fields Manager")
    print("=" * 60)

    if len(sys.argv) < 2:
        print("\nUsage: python subscriber_fields.py <command> [args]")
        print("\nCommands:")
        print("  field add <name> [type]       - Add custom field")
        print("  field list                    - List all fields")
        print("  subscriber add <email>        - Add subscriber")
        print("  subscriber list               - List subscribers")
        print("  subscriber get <email>        - Get subscriber details")
        print("  tag add <email> <tag>         - Add tag to subscriber")
        print("  stats                         - Show statistics")
        print("  export <file>                 - Export to CSV")
        print("  import <file>                 - Import from CSV")
        sys.exit(0)

    command = sys.argv[1]

    if command == 'field' and len(sys.argv) > 2:
        subcommand = sys.argv[2]
        
        if subcommand == 'add' and len(sys.argv) > 3:
            name = sys.argv[3]
            field_type = sys.argv[4] if len(sys.argv) > 4 else 'text'
            field = manager.add_field_definition(name, field_type)
            if 'error' in field:
                print(f"✗ {field['error']}")
            else:
                print(f"✓ Field added: {field['name']} ({field['type']})")
        
        elif subcommand == 'list':
            fields = manager.get_field_definitions()
            print(f"\nCustom Fields ({len(fields)}):")
            for field in fields:
                print(f"  - {field['name']} ({field['type']}) - {field['label']}")
    
    elif command == 'subscriber' and len(sys.argv) > 2:
        subcommand = sys.argv[2]
        
        if subcommand == 'add' and len(sys.argv) > 3:
            email = sys.argv[3]
            result = manager.add_subscriber(email)
            if 'error' in result:
                print(f"✗ {result['error']}")
            else:
                print(f"✓ Subscriber added: {email}")
        
        elif subcommand == 'list':
            subs = manager.list_subscribers(20)
            print(f"\nSubscribers ({len(subs)}):")
            for sub in subs:
                print(f"  - {sub['email']}")
        
        elif subcommand == 'get' and len(sys.argv) > 3:
            sub = manager.get_subscriber(sys.argv[3])
            if sub:
                print(f"\nSubscriber: {sub['email']}")
                for key, value in sub.items():
                    print(f"  {key}: {value}")
            else:
                print("Subscriber not found")
    
    elif command == 'tag' and len(sys.argv) > 3:
        email = sys.argv[2]
        tag = sys.argv[3]
        if manager.add_tag(email, tag):
            print(f"✓ Tag '{tag}' added to {email}")
        else:
            print("Subscriber not found")
    
    elif command == 'stats':
        stats = manager.get_statistics()
        print(f"\nSubscriber Statistics:")
        print(f"  Total: {stats['total']}")
        print(f"  With custom fields: {stats['with_fields']}")
        print(f"  Unique tags: {stats['tags_count']}")
        print(f"  Recent (7 days): {stats['recent_signups_7d']}")
        print(f"  Recent (30 days): {stats['recent_signups_30d']}")
    
    elif command == 'export' and len(sys.argv) > 2:
        from pathlib import Path
        count = manager.export_subscribers(Path(sys.argv[2]))
        print(f"✓ Exported {count} subscribers to {sys.argv[2]}")
    
    elif command == 'import' and len(sys.argv) > 2:
        from pathlib import Path
        count = manager.import_subscribers(Path(sys.argv[2]))
        print(f"✓ Imported {count} subscribers from {sys.argv[2]}")
    
    else:
        print(f"Unknown command: {command}")
