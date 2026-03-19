"""Template Manager - Clone, manage, and organize email templates."""
import shutil
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional


class TemplateManager:
    """Manage email templates with cloning and organization features."""

    def __init__(self, template_dir: Path = None):
        if template_dir is None:
            template_dir = Path(__file__).parent / 'templates'
        
        self.template_dir = template_dir
        self.template_dir.mkdir(parents=True, exist_ok=True)

    def list_templates(self) -> List[dict]:
        """List all available templates with metadata."""
        templates = []

        for html_file in sorted(self.template_dir.glob("*.html")):
            if html_file.name.endswith('_subject.html'):
                continue

            name = html_file.stem
            subject_file = self.template_dir / f"{name}_subject.txt"

            template_info = {
                'name': name,
                'html_file': str(html_file),
                'subject_file': str(subject_file) if subject_file.exists() else None,
                'created_at': datetime.fromtimestamp(html_file.stat().st_ctime).isoformat(),
                'modified_at': datetime.fromtimestamp(html_file.stat().st_mtime).isoformat(),
                'size_bytes': html_file.stat().st_size,
                'subject': None,
                'category': self._detect_category(name)
            }

            if subject_file.exists():
                with open(subject_file, 'r', encoding='utf-8') as f:
                    template_info['subject'] = f.read().strip()

            templates.append(template_info)

        return templates

    def _detect_category(self, template_name: str) -> str:
        """Detect template category based on name patterns."""
        name_lower = template_name.lower()

        categories = {
            'promotion': ['flash', 'sale', 'promo', 'discount', 'offer', 'deal', 'bold', 'vibrant'],
            'business': ['pro', 'corporate', 'business', 'tech', 'minimal', 'elegant'],
            'personal': ['friendly', 'warm', 'casual', 'personal', 'playful', 'fresh'],
            'dark': ['dark', 'neon', 'night'],
            'luxury': ['luxury', 'premium', 'gold', 'elegant'],
        }

        for category, keywords in categories.items():
            if any(kw in name_lower for kw in keywords):
                return category

        return 'general'

    def get_template(self, name: str) -> Optional[dict]:
        """Get template details by name."""
        html_file = self.template_dir / f"{name}.html"
        subject_file = self.template_dir / f"{name}_subject.txt"

        if not html_file.exists():
            return None

        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()

        subject = None
        if subject_file.exists():
            with open(subject_file, 'r', encoding='utf-8') as f:
                subject = f.read().strip()

        return {
            'name': name,
            'html': html_content,
            'subject': subject,
            'html_file': str(html_file),
            'subject_file': str(subject_file) if subject_file.exists() else None,
            'size_bytes': len(html_content),
            'category': self._detect_category(name)
        }

    def clone_template(
        self,
        source_name: str,
        new_name: str,
        new_subject: str = None
    ) -> bool:
        """
        Clone an existing template with a new name.

        Args:
            source_name: Name of template to clone
            new_name: Name for the new template
            new_subject: Optional new subject line

        Returns:
            True if successful
        """
        source = self.get_template(source_name)
        if not source:
            raise ValueError(f"Template not found: {source_name}")

        # Check if new name already exists
        if (self.template_dir / f"{new_name}.html").exists():
            raise ValueError(f"Template already exists: {new_name}")

        # Copy HTML file
        source_html = self.template_dir / f"{source_name}.html"
        dest_html = self.template_dir / f"{new_name}.html"
        shutil.copy2(source_html, dest_html)

        # Copy or create subject file
        source_subject = self.template_dir / f"{source_name}_subject.txt"
        dest_subject = self.template_dir / f"{new_name}_subject.txt"

        if new_subject:
            with open(dest_subject, 'w', encoding='utf-8') as f:
                f.write(new_subject)
        elif source_subject.exists():
            shutil.copy2(source_subject, dest_subject)

        return True

    def create_template(
        self,
        name: str,
        html_content: str,
        subject: str = None,
        base_template: str = None
    ) -> bool:
        """
        Create a new template.

        Args:
            name: Template name
            html_content: HTML content
            subject: Optional subject line
            base_template: Optional base template to start from

        Returns:
            True if successful
        """
        if (self.template_dir / f"{name}.html").exists():
            raise ValueError(f"Template already exists: {name}")

        # If base template specified, load and modify it
        if base_template:
            base = self.get_template(base_template)
            if base:
                html_content = base['html']

        # Write HTML file
        html_file = self.template_dir / f"{name}.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        # Write subject file if provided
        if subject:
            subject_file = self.template_dir / f"{name}_subject.txt"
            with open(subject_file, 'w', encoding='utf-8') as f:
                f.write(subject)

        return True

    def update_template(
        self,
        name: str,
        html_content: str = None,
        subject: str = None
    ) -> bool:
        """Update an existing template."""
        template = self.get_template(name)
        if not template:
            raise ValueError(f"Template not found: {name}")

        if html_content:
            html_file = self.template_dir / f"{name}.html"
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)

        if subject is not None:
            subject_file = self.template_dir / f"{name}_subject.txt"
            if subject:
                with open(subject_file, 'w', encoding='utf-8') as f:
                    f.write(subject)
            elif subject_file.exists():
                subject_file.unlink()

        return True

    def delete_template(self, name: str) -> bool:
        """Delete a template."""
        html_file = self.template_dir / f"{name}.html"
        subject_file = self.template_dir / f"{name}_subject.txt"

        if not html_file.exists():
            return False

        html_file.unlink()
        if subject_file.exists():
            subject_file.unlink()

        return True

    def rename_template(self, old_name: str, new_name: str) -> bool:
        """Rename a template."""
        if not (self.template_dir / f"{old_name}.html").exists():
            raise ValueError(f"Template not found: {old_name}")

        if (self.template_dir / f"{new_name}.html").exists():
            raise ValueError(f"Template already exists: {new_name}")

        # Rename HTML file
        old_html = self.template_dir / f"{old_name}.html"
        new_html = self.template_dir / f"{new_name}.html"
        old_html.rename(new_html)

        # Rename subject file if exists
        old_subject = self.template_dir / f"{old_name}_subject.txt"
        new_subject = self.template_dir / f"{new_name}_subject.txt"
        if old_subject.exists():
            old_subject.rename(new_subject)

        return True

    def get_template_variables(self, name: str) -> List[str]:
        """Extract variable placeholders from a template."""
        template = self.get_template(name)
        if not template:
            return []

        # Find $variable patterns
        pattern = r'\$(\w+)'
        variables = set(re.findall(pattern, template['html']))

        if template['subject']:
            variables.update(re.findall(pattern, template['subject']))

        return sorted(list(variables))

    def search_templates(self, query: str) -> List[dict]:
        """Search templates by name, subject, or content."""
        results = []
        query_lower = query.lower()

        for template in self.list_templates():
            # Search in name
            if query_lower in template['name'].lower():
                results.append(template)
                continue

            # Search in subject
            if template['subject'] and query_lower in template['subject'].lower():
                results.append(template)
                continue

            # Search in content
            template_data = self.get_template(template['name'])
            if template_data and query_lower in template_data['html'].lower():
                results.append(template)

        return results

    def get_templates_by_category(self, category: str) -> List[dict]:
        """Get templates by category."""
        return [t for t in self.list_templates() if t['category'] == category]

    def export_template(self, name: str, output_file: Path) -> Path:
        """Export a template to a file."""
        template = self.get_template(name)
        if not template:
            raise ValueError(f"Template not found: {name}")

        import json

        export_data = {
            'name': name,
            'subject': template['subject'],
            'html': template['html'],
            'category': template['category'],
            'exported_at': datetime.now().isoformat()
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2)

        return output_file

    def import_template(self, input_file: Path, overwrite: bool = False) -> str:
        """Import a template from a file."""
        import json

        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        name = data.get('name')
        if not name:
            raise ValueError("Invalid template file: missing 'name' field")

        if (self.template_dir / f"{name}.html").exists() and not overwrite:
            raise ValueError(f"Template already exists: {name}. Use overwrite=True to replace.")

        html_content = data.get('html', '')
        subject = data.get('subject')

        self.create_template(name, html_content, subject)

        return name

    def get_template_stats(self) -> dict:
        """Get statistics about templates."""
        templates = self.list_templates()

        stats = {
            'total': len(templates),
            'by_category': {},
            'total_size_bytes': 0,
            'avg_size_bytes': 0,
            'with_subject': 0,
            'without_subject': 0
        }

        for template in templates:
            # Count by category
            cat = template['category']
            stats['by_category'][cat] = stats['by_category'].get(cat, 0) + 1

            # Size stats
            stats['total_size_bytes'] += template['size_bytes']

            # Subject stats
            if template['subject']:
                stats['with_subject'] += 1
            else:
                stats['without_subject'] += 1

        if stats['total'] > 0:
            stats['avg_size_bytes'] = stats['total_size_bytes'] // stats['total']

        return stats


if __name__ == '__main__':
    import sys

    print("=" * 60)
    print("Template Manager")
    print("=" * 60)

    manager = TemplateManager()

    if len(sys.argv) < 2:
        print("\nUsage: python template_manager.py <command> [args]")
        print("\nCommands:")
        print("  list                      - List all templates")
        print("  info <name>               - Show template details")
        print("  clone <source> <new>      - Clone a template")
        print("  delete <name>             - Delete a template")
        print("  rename <old> <new>        - Rename a template")
        print("  search <query>            - Search templates")
        print("  category <name>           - Get templates by category")
        print("  variables <name>          - Show template variables")
        print("  export <name> <file>      - Export template to JSON")
        print("  import <file>             - Import template from JSON")
        print("  stats                     - Show template statistics")
        sys.exit(0)

    command = sys.argv[1]

    if command == 'list':
        templates = manager.list_templates()
        if not templates:
            print("\nNo templates found")
        else:
            print(f"\n{'Name':<20} {'Subject':<35} {'Category':<12} {'Size':<10}")
            print("-" * 80)
            for t in templates:
                subject = (t['subject'][:32] + '...') if t['subject'] and len(t['subject']) > 32 else (t['subject'] or 'N/A')
                print(f"{t['name']:<20} {subject:<35} {t['category']:<12} {t['size_bytes']:,} bytes")

    elif command == 'info' and len(sys.argv) > 2:
        name = sys.argv[2]
        template = manager.get_template(name)
        if template:
            print(f"\n{'='*50}")
            print(f"Template: {name}")
            print(f"{'='*50}")
            print(f"Category: {template['category']}")
            print(f"Subject: {template['subject'] or 'N/A'}")
            print(f"Size: {template['size_bytes']:,} bytes")
            print(f"Created: {template['created_at']}")
            print(f"Modified: {template['modified_at']}")
            print(f"\nHTML Preview (first 500 chars):")
            print("-" * 50)
            print(template['html'][:500])
            print("...")
            print(f"{'='*50}")
        else:
            print(f"✗ Template not found: {name}")

    elif command == 'clone' and len(sys.argv) >= 4:
        source = sys.argv[2]
        new_name = sys.argv[3]
        new_subject = sys.argv[4] if len(sys.argv) > 4 else None
        try:
            manager.clone_template(source, new_name, new_subject)
            print(f"✓ Cloned '{source}' to '{new_name}'")
        except ValueError as e:
            print(f"✗ Error: {e}")

    elif command == 'delete' and len(sys.argv) > 2:
        name = sys.argv[2]
        if manager.delete_template(name):
            print(f"✓ Deleted template: {name}")
        else:
            print(f"✗ Template not found: {name}")

    elif command == 'rename' and len(sys.argv) >= 4:
        old_name = sys.argv[2]
        new_name = sys.argv[3]
        try:
            manager.rename_template(old_name, new_name)
            print(f"✓ Renamed '{old_name}' to '{new_name}'")
        except ValueError as e:
            print(f"✗ Error: {e}")

    elif command == 'search' and len(sys.argv) > 2:
        query = sys.argv[2]
        results = manager.search_templates(query)
        if results:
            print(f"\nFound {len(results)} template(s) matching '{query}':")
            for t in results:
                print(f"  - {t['name']} ({t['category']})")
        else:
            print(f"\nNo templates found matching '{query}'")

    elif command == 'category' and len(sys.argv) > 2:
        category = sys.argv[2]
        templates = manager.get_templates_by_category(category)
        if templates:
            print(f"\nTemplates in category '{category}':")
            for t in templates:
                print(f"  - {t['name']}: {t['subject'] or 'No subject'}")
        else:
            print(f"\nNo templates found in category '{category}'")

    elif command == 'variables' and len(sys.argv) > 2:
        name = sys.argv[2]
        variables = manager.get_template_variables(name)
        if variables:
            print(f"\nVariables in template '{name}':")
            for var in variables:
                print(f"  ${var}")
        else:
            print(f"\nNo variables found in template '{name}'")

    elif command == 'export' and len(sys.argv) >= 4:
        name = sys.argv[2]
        output_file = Path(sys.argv[3])
        try:
            manager.export_template(name, output_file)
            print(f"✓ Exported template to {output_file}")
        except ValueError as e:
            print(f"✗ Error: {e}")

    elif command == 'import' and len(sys.argv) > 2:
        input_file = Path(sys.argv[2])
        try:
            name = manager.import_template(input_file)
            print(f"✓ Imported template: {name}")
        except ValueError as e:
            print(f"✗ Error: {e}")

    elif command == 'stats':
        stats = manager.get_template_stats()
        print(f"\nTemplate Statistics:")
        print(f"  Total Templates: {stats['total']}")
        print(f"  With Subject: {stats['with_subject']}")
        print(f"  Without Subject: {stats['without_subject']}")
        print(f"  Total Size: {stats['total_size_bytes']:,} bytes")
        print(f"  Avg Size: {stats['avg_size_bytes']:,} bytes")
        print(f"  By Category: {stats['by_category']}")

    else:
        print(f"Unknown command: {command}")
        print("Run without arguments to see usage")
