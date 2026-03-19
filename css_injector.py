"""Custom CSS Injector - Add custom styles to email templates."""
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional


class CSSInjector:
    """Inject custom CSS styles into email templates."""

    # Common email-safe CSS properties
    SAFE_PROPERTIES = [
        'color', 'background-color', 'background', 'font-family', 'font-size',
        'font-weight', 'font-style', 'text-decoration', 'text-align', 'line-height',
        'letter-spacing', 'margin', 'padding', 'border', 'border-radius',
        'width', 'height', 'max-width', 'min-width', 'display', 'position',
        'top', 'right', 'bottom', 'left', 'float', 'clear', 'overflow',
        'visibility', 'opacity', 'vertical-align', 'table-layout', 'border-collapse',
        'border-spacing', 'cellpadding', 'cellspacing'
    ]

    # Unsafe properties that should be stripped
    UNSAFE_PROPERTIES = [
        'behavior', 'binding', 'transition', 'animation', 'transform',
        'filter', 'clip-path', 'mask', 'mix-blend-mode'
    ]

    def __init__(self, styles_dir: Path = None):
        if styles_dir is None:
            styles_dir = Path(__file__).parent / 'styles'
        
        self.styles_dir = styles_dir
        self.styles_dir.mkdir(parents=True, exist_ok=True)
        self._presets = self._load_presets()

    def _load_presets(self) -> Dict[str, str]:
        """Load built-in CSS presets."""
        return {
            'dark_mode': '''
/* Dark Mode Overrides */
body, .body { background-color: #1a1a2e !important; color: #eee !important; }
.container { background-color: #16213e !important; }
.header { background: linear-gradient(135deg, #1a1a2e 0%, #0f0f23 100%) !important; }
.content { background-color: #16213e !important; color: #eee !important; }
.footer { background-color: #0f0f23 !important; color: #aaa !important; }
a { color: #667eea !important; }
h1, h2, h3 { color: #fff !important; }
p { color: #ddd !important; }
''',
            'compact': '''
/* Compact Spacing */
.container { padding: 10px !important; max-width: 500px !important; }
.content { padding: 15px !important; }
.header { padding: 15px !important; }
.footer { padding: 10px !important; font-size: 11px !important; }
h1 { font-size: 20px !important; margin: 10px 0 !important; }
h2 { font-size: 18px !important; margin: 8px 0 !important; }
p { margin: 8px 0 !important; font-size: 14px !important; }
''',
            'bold_colors': '''
/* Bold Color Scheme */
.header { background: linear-gradient(135deg, #ff6b6b 0%, #feca57 100%) !important; }
.cta-button { background-color: #ff6b6b !important; box-shadow: 0 4px 15px rgba(255,107,107,0.4) !important; }
a { color: #ff6b6b !important; }
.highlight { color: #feca57 !important; }
''',
            'minimal': '''
/* Minimal Style */
.container { background-color: #fff !important; border: 1px solid #eee !important; }
.header { background-color: #f8f9fa !important; color: #333 !important; border-bottom: 2px solid #eee !important; }
.content { padding: 30px 20px !important; }
.cta-button { background-color: #333 !important; color: #fff !important; border-radius: 3px !important; }
.footer { background-color: #f8f9fa !important; color: #666 !important; }
''',
            'corporate': '''
/* Corporate Blue Theme */
.header { background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%) !important; }
.cta-button { background-color: #1e3c72 !important; }
a { color: #1e3c72 !important; }
.container { border-top: 4px solid #1e3c72 !important; }
''',
            'warm': '''
/* Warm Orange Theme */
.header { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%) !important; }
.cta-button { background-color: #f5576c !important; }
a { color: #f5576c !important; }
.highlight { color: #f093fb !important; }
''',
            'large_text': '''
/* Large Text for Accessibility */
body, .body { font-size: 18px !important; line-height: 1.8 !important; }
h1 { font-size: 32px !important; }
h2 { font-size: 26px !important; }
p { font-size: 18px !important; }
.cta-button { padding: 20px 50px !important; font-size: 18px !important; }
''',
            'high_contrast': '''
/* High Contrast for Accessibility */
body { background-color: #000 !important; color: #fff !important; }
.container { background-color: #111 !important; }
.content { background-color: #111 !important; color: #fff !important; }
a { color: #00ff00 !important; text-decoration: underline !important; }
.cta-button { background-color: #00ff00 !important; color: #000 !important; border: 2px solid #00ff00 !important; }
.header { border-bottom: 2px solid #fff !important; }
'''
        }

    def inject_css(self, html_content: str, css: str, inline: bool = True) -> str:
        """
        Inject CSS into HTML email template.

        Args:
            html_content: Original HTML content
            css: CSS to inject
            inline: If True, inline CSS into style attributes

        Returns:
            Modified HTML content
        """
        # Sanitize CSS
        css = self._sanitize_css(css)

        if inline:
            return self._inline_css(html_content, css)
        else:
            return self._inject_style_tag(html_content, css)

    def _sanitize_css(self, css: str) -> str:
        """Remove unsafe CSS properties."""
        sanitized = css

        # Remove unsafe properties
        for prop in self.UNSAFE_PROPERTIES:
            pattern = rf'{prop}\s*:[^;]+;'
            sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)

        # Remove @import rules (security risk)
        sanitized = re.sub(r'@import[^;]+;', '', sanitized, flags=re.IGNORECASE)

        # Remove @media queries for basic inline injection
        # (They're preserved when using style tag injection)
        
        return sanitized

    def _inline_css(self, html_content: str, css: str) -> str:
        """
        Inline CSS into HTML style attributes.
        
        This is the most compatible approach for email clients.
        """
        # Parse CSS rules
        rules = self._parse_css_rules(css)

        result = html_content

        for selector, properties in rules.items():
            # Convert selector to elements
            elements = self._find_elements_by_selector(result, selector)

            for element in elements:
                # Get existing style
                existing_style = self._get_element_style(element)

                # Merge with new properties
                new_style = self._merge_styles(existing_style, properties)

                # Update element
                result = self._update_element_style(result, element, new_style)

        return result

    def _inject_style_tag(self, html_content: str, css: str) -> str:
        """Inject CSS as a <style> tag in the <head>."""
        style_tag = f'<style type="text/css">\n{css}\n</style>'

        # Try to insert in head
        if '<head>' in html_content:
            return html_content.replace('<head>', f'<head>\n{style_tag}')
        elif '<HEAD>' in html_content:
            return html_content.replace('<HEAD>', f'<HEAD>\n{style_tag}')

        # No head tag - insert at beginning
        return style_tag + '\n' + html_content

    def _parse_css_rules(self, css: str) -> Dict[str, Dict[str, str]]:
        """Parse CSS into selector -> properties dict."""
        rules = {}

        # Simple CSS parser
        pattern = r'([^{]+)\{([^}]+)\}'
        matches = re.findall(pattern, css)

        for selector, properties in matches:
            selector = selector.strip()
            props = {}

            for prop in properties.split(';'):
                if ':' in prop:
                    key, value = prop.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    if key and value:
                        props[key] = value

            if props:
                rules[selector] = props

        return rules

    def _find_elements_by_selector(self, html: str, selector: str) -> List[str]:
        """Find HTML elements matching a CSS selector."""
        elements = []

        # Handle class selectors
        if selector.startswith('.'):
            class_name = selector[1:]
            pattern = rf'class=["\'][^"\']*{class_name}[^"\']*["\']'
            matches = re.findall(pattern, html, re.IGNORECASE)
            elements.extend(matches)

        # Handle ID selectors
        elif selector.startswith('#'):
            id_name = selector[1:]
            pattern = rf'id=["\']{id_name}["\']'
            matches = re.findall(pattern, html, re.IGNORECASE)
            elements.extend(matches)

        # Handle element selectors
        else:
            tag = selector.split('.')[0].split('#')[0]
            pattern = rf'<{tag}[^>]*>'
            matches = re.findall(pattern, html, re.IGNORECASE)
            elements.extend(matches)

        return elements

    def _get_element_style(self, element: str) -> Dict[str, str]:
        """Extract style properties from an HTML element."""
        style_match = re.search(r'style=["\']([^"\']+)["\']', element, re.IGNORECASE)
        if not style_match:
            return {}

        styles = {}
        for prop in style_match.group(1).split(';'):
            if ':' in prop:
                key, value = prop.split(':', 1)
                styles[key.strip()] = value.strip()

        return styles

    def _merge_styles(
        self, 
        existing: Dict[str, str], 
        new: Dict[str, str]
    ) -> Dict[str, str]:
        """Merge existing and new styles, new takes precedence."""
        merged = existing.copy()
        merged.update(new)
        return merged

    def _update_element_style(
        self, 
        html: str, 
        element: str, 
        styles: Dict[str, str]
    ) -> str:
        """Update an element's style attribute in HTML."""
        style_string = '; '.join(f'{k}: {v}' for k, v in styles.items())
        new_element = re.sub(
            r'style=["\'][^"\']*["\']',
            f'style="{style_string}"',
            element,
            flags=re.IGNORECASE
        )

        # If no existing style, add it
        if 'style=' not in new_element:
            new_element = re.sub(
                r'<(\w+)',
                f'<\\1 style="{style_string}"',
                element,
                count=1,
                flags=re.IGNORECASE
            )

        return html.replace(element, new_element, 1)

    def apply_preset(self, html_content: str, preset_name: str) -> str:
        """Apply a built-in CSS preset to HTML."""
        if preset_name not in self._presets:
            raise ValueError(f"Unknown preset: {preset_name}")

        css = self._presets[preset_name]
        return self.inject_css(html_content, css, inline=False)

    def list_presets(self) -> List[str]:
        """List available CSS presets."""
        return list(self._presets.keys())

    def get_preset(self, name: str) -> Optional[str]:
        """Get a preset by name."""
        return self._presets.get(name)

    def save_custom_preset(self, name: str, css: str) -> Path:
        """Save a custom CSS preset."""
        file_path = self.styles_dir / f"{name}.css"

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"/* Custom Preset: {name} */\n")
            f.write(f"/* Created: {datetime.now().isoformat()} */\n\n")
            f.write(css)

        return file_path

    def load_custom_preset(self, name: str) -> Optional[str]:
        """Load a custom CSS preset."""
        file_path = self.styles_dir / f"{name}.css"

        if not file_path.exists():
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def list_custom_presets(self) -> List[str]:
        """List custom CSS presets."""
        presets = []
        for css_file in self.styles_dir.glob("*.css"):
            presets.append(css_file.stem)
        return presets

    def create_color_scheme(
        self,
        primary_color: str,
        secondary_color: str = None,
        background_color: str = '#ffffff',
        text_color: str = '#333333'
    ) -> str:
        """
        Generate a CSS color scheme.

        Args:
            primary_color: Main brand color
            secondary_color: Accent color (optional)
            background_color: Background color
            text_color: Text color

        Returns:
            CSS string
        """
        secondary = secondary_color or primary_color

        return f'''
/* Color Scheme */
.header {{
    background: linear-gradient(135deg, {primary_color} 0%, {secondary} 100%) !important;
}}

.cta-button {{
    background-color: {primary_color} !important;
    color: #ffffff !important;
}}

a {{
    color: {primary_color} !important;
}}

.container {{
    background-color: {background_color} !important;
}}

.content {{
    color: {text_color} !important;
}}

.highlight {{
    color: {secondary} !important;
}}

.footer {{
    background-color: #f8f9fa !important;
    color: #666666 !important;
}}
'''

    def create_responsive_css(self) -> str:
        """Generate responsive CSS for email templates."""
        return '''
/* Responsive Styles */
@media only screen and (max-width: 600px) {
    .container {
        width: 100% !important;
        max-width: 100% !important;
    }
    
    .content {
        padding: 15px !important;
    }
    
    .header h1 {
        font-size: 24px !important;
    }
    
    .cta-button {
        display: block !important;
        width: 100% !important;
        padding: 15px 0 !important;
        text-align: center !important;
    }
    
    .two-column {
        display: block !important;
        width: 100% !important;
    }
    
    .image-full {
        width: 100% !important;
        height: auto !important;
    }
}
'''


if __name__ == '__main__':
    import sys

    print("=" * 60)
    print("CSS Injector")
    print("=" * 60)

    injector = CSSInjector()

    if len(sys.argv) < 2:
        print("\nUsage: python css_injector.py <command> [args]")
        print("\nCommands:")
        print("  presets                 - List available presets")
        print("  preview <preset>        - Preview a preset's CSS")
        print("  apply <template> <preset> - Apply preset to template")
        print("  colors <primary> [secondary] - Generate color scheme")
        print("  responsive              - Generate responsive CSS")
        print("  save <name> <file>      - Save custom preset from file")
        print("  list-custom             - List custom presets")
        sys.exit(0)

    command = sys.argv[1]

    if command == 'presets':
        presets = injector.list_presets()
        print(f"\nAvailable Presets:")
        for preset in presets:
            print(f"  - {preset}")

    elif command == 'preview' and len(sys.argv) > 2:
        preset_name = sys.argv[2]
        css = injector.get_preset(preset_name)
        if css:
            print(f"\n/* {preset_name} */")
            print(css)
        else:
            print(f"✗ Preset not found: {preset_name}")

    elif command == 'apply' and len(sys.argv) >= 4:
        template_name = sys.argv[2]
        preset_name = sys.argv[3]

        template_dir = Path(__file__).parent / 'templates'
        template_file = template_dir / f"{template_name}.html"

        if not template_file.exists():
            print(f"✗ Template not found: {template_name}")
            sys.exit(1)

        with open(template_file, 'r', encoding='utf-8') as f:
            html = f.read()

        css = injector.get_preset(preset_name)
        if not css:
            print(f"✗ Preset not found: {preset_name}")
            sys.exit(1)

        result = injector.inject_css(html, css, inline=False)

        # Save to new file
        output_file = template_dir / f"{template_name}_{preset_name}.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result)

        print(f"✓ Applied '{preset_name}' to '{template_name}'")
        print(f"  Output: {output_file}")

    elif command == 'colors' and len(sys.argv) > 2:
        primary = sys.argv[2]
        secondary = sys.argv[3] if len(sys.argv) > 3 else None

        css = injector.create_color_scheme(primary, secondary)
        print("\n/* Generated Color Scheme */")
        print(css)

    elif command == 'responsive':
        css = injector.create_responsive_css()
        print("\n/* Responsive CSS */")
        print(css)

    elif command == 'save' and len(sys.argv) >= 4:
        name = sys.argv[2]
        file_path = Path(sys.argv[3])

        if not file_path.exists():
            print(f"✗ File not found: {file_path}")
            sys.exit(1)

        with open(file_path, 'r', encoding='utf-8') as f:
            css = f.read()

        output_path = injector.save_custom_preset(name, css)
        print(f"✓ Saved custom preset: {output_path}")

    elif command == 'list-custom':
        custom = injector.list_custom_presets()
        if custom:
            print(f"\nCustom Presets:")
            for preset in custom:
                print(f"  - {preset}")
        else:
            print("\nNo custom presets found")

    else:
        print(f"Unknown command: {command}")
        print("Run without arguments to see usage")
