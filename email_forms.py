"""Email Form Generator - Create popup and inline signup forms."""
from pathlib import Path
from typing import Dict, List
from datetime import datetime


class EmailFormGenerator:
    """Generate email signup forms (popup, inline, floating)."""

    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or Path(__file__).parent / 'forms'
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_inline_form(self, config: Dict = None) -> str:
        """Generate inline signup form."""
        config = config or {}
        brand_color = config.get('brand_color', '#667eea')
        title = config.get('title', 'Subscribe to Our Newsletter')
        description = config.get('description', 'Get the latest updates and offers')
        button_text = config.get('button_text', 'Subscribe')
        placeholder = config.get('placeholder', 'Enter your email')

        return f"""<!-- Email Inline Form -->
<div class="email-signup-form" style="max-width: 500px; margin: 40px auto; padding: 30px; background: #f8f9fa; border-radius: 10px; font-family: Arial, sans-serif;">
    <h3 style="margin: 0 0 10px 0; color: {brand_color};">{title}</h3>
    <p style="margin: 0 0 20px 0; color: #666; font-size: 14px;">{description}</p>
    
    <form id="emailSignupForm" onsubmit="handleSignup(event); return false;" style="display: flex; gap: 10px; flex-wrap: wrap;">
        <input type="email" 
               name="email" 
               placeholder="{placeholder}" 
               required
               style="flex: 1; min-width: 200px; padding: 12px 15px; border: 2px solid #e0e0e0; border-radius: 5px; font-size: 14px;" />
        
        <button type="submit" 
                style="padding: 12px 30px; background: {brand_color}; color: white; border: none; border-radius: 5px; font-size: 14px; font-weight: 600; cursor: pointer; transition: opacity 0.3s;">
            {button_text}
        </button>
    </form>
    
    <p style="margin: 15px 0 0 0; font-size: 12px; color: #888;">
        🔒 We respect your privacy. Unsubscribe at any time.
    </p>
</div>

<script>
function handleSignup(event) {{
    event.preventDefault();
    const form = event.target;
    const email = form.email.value;
    
    // Send to your server
    fetch('/api/subscribe', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{ email }})
    }})
    .then(response => response.json())
    .then(data => {{
        if (data.success) {{
            form.innerHTML = '<p style="color: #28a745; font-weight: 600;">✓ Thank you for subscribing!</p>';
        }} else {{
            alert('Error: ' + data.message);
        }}
    }})
    .catch(error => {{
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
    }});
}}
</script>
<!-- End Email Inline Form -->"""

    def generate_popup_form(self, config: Dict = None) -> str:
        """Generate exit-intent popup form."""
        config = config or {}
        brand_color = config.get('brand_color', '#667eea')
        title = config.get('title', 'Wait! Before You Go...')
        description = config.get('description', 'Get 10% off your first order when you subscribe!')
        button_text = config.get('button_text', 'Get My Discount')
        placeholder = config.get('placeholder', 'Enter your email')

        return f"""<!-- Email Popup Form (Exit Intent) -->
<div id="emailPopupOverlay" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.7); z-index: 9999; align-items: center; justify-content: center;">
    <div class="email-popup" style="background: white; max-width: 450px; width: 90%; border-radius: 15px; overflow: hidden; box-shadow: 0 20px 60px rgba(0,0,0,0.3); position: relative; animation: popupSlide 0.3s ease-out;">
        <button onclick="closePopup()" style="position: absolute; top: 15px; right: 15px; background: none; border: none; font-size: 24px; cursor: pointer; color: #888; z-index: 10;">&times;</button>
        
        <div style="background: {brand_color}; color: white; padding: 30px; text-align: center;">
            <h2 style="margin: 0; font-size: 24px;">{title}</h2>
        </div>
        
        <div style="padding: 30px; text-align: center;">
            <p style="margin: 0 0 25px 0; color: #666; font-size: 15px; line-height: 1.6;">{description}</p>
            
            <form id="popupSignupForm" onsubmit="handlePopupSignup(event); return false;" style="display: flex; flex-direction: column; gap: 15px;">
                <input type="email" 
                       name="email" 
                       placeholder="{placeholder}" 
                       required
                       style="padding: 15px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 15px; text-align: center;" />
                
                <button type="submit" 
                        style="padding: 15px; background: {brand_color}; color: white; border: none; border-radius: 8px; font-size: 16px; font-weight: 600; cursor: pointer;">
                    {button_text}
                </button>
            </form>
            
            <p style="margin: 20px 0 0 0; font-size: 12px; color: #888;">
                📧 Join 10,000+ subscribers • No spam, ever
            </p>
        </div>
    </div>
</div>

<style>
@keyframes popupSlide {{
    from {{ opacity: 0; transform: translateY(-20px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}
</style>

<script>
// Show popup on exit intent
let popupShown = false;
const overlay = document.getElementById('emailPopupOverlay');

function showPopup() {{
    if (!popupShown) {{
        popupShown = true;
        overlay.style.display = 'flex';
    }}
}}

function closePopup() {{
    overlay.style.display = 'none';
}}

// Exit intent detection
document.addEventListener('mouseleave', (e) => {{
    if (e.clientY <= 0) {{
        showPopup();
    }}
}});

// Show after delay (alternative trigger)
setTimeout(() => {{
    if (!popupShown) showPopup();
}}, 5000);

// Handle signup
function handlePopupSignup(event) {{
    event.preventDefault();
    const form = event.target;
    const email = form.email.value;
    
    fetch('/api/subscribe', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{ email }})
    }})
    .then(response => response.json())
    .then(data => {{
        if (data.success) {{
            form.innerHTML = '<p style="color: #28a745; font-size: 18px; font-weight: 600;">✓ Success! Check your email for the discount code.</p>';
            setTimeout(closePopup, 3000);
        }}
    }});
}}

// Close on overlay click
overlay.addEventListener('click', (e) => {{
    if (e.target === overlay) closePopup();
}});
</script>
<!-- End Email Popup Form -->"""

    def generate_floating_bar(self, config: Dict = None) -> str:
        """Generate floating signup bar."""
        config = config or {}
        brand_color = config.get('brand_color', '#667eea')
        text = config.get('text', 'Join our newsletter for exclusive deals!')
        button_text = config.get('button_text', 'Subscribe')
        placeholder = config.get('placeholder', 'Your email')

        return f"""<!-- Floating Signup Bar -->
<div id="floatingSignupBar" style="position: fixed; bottom: 0; left: 0; right: 0; background: white; box-shadow: 0 -5px 20px rgba(0,0,0,0.1); padding: 15px 30px; display: flex; align-items: center; justify-content: center; gap: 15px; z-index: 999; flex-wrap: wrap;">
    <span style="color: #333; font-size: 14px; font-weight: 500;">{text}</span>
    
    <form id="floatingForm" onsubmit="handleFloatingSignup(event); return false;" style="display: flex; gap: 10px; flex-wrap: wrap;">
        <input type="email" 
               name="email" 
               placeholder="{placeholder}" 
               required
               style="padding: 10px 15px; border: 2px solid #e0e0e0; border-radius: 5px; font-size: 14px; min-width: 200px;" />
        
        <button type="submit" 
                style="padding: 10px 25px; background: {brand_color}; color: white; border: none; border-radius: 5px; font-size: 14px; font-weight: 600; cursor: pointer;">
            {button_text}
        </button>
        
        <button type="button" 
                onclick="closeFloatingBar()" 
                style="padding: 10px 15px; background: none; border: none; font-size: 20px; cursor: pointer; color: #888;">
            &times;
        </button>
    </form>
</div>

<script>
function handleFloatingSignup(event) {{
    event.preventDefault();
    const form = event.target;
    const email = form.email.value;
    
    fetch('/api/subscribe', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{ email }})
    }})
    .then(response => response.json())
    .then(data => {{
        if (data.success) {{
            closeFloatingBar();
            alert('✓ Thank you for subscribing!');
        }}
    }});
}}

function closeFloatingBar() {{
    document.getElementById('floatingSignupBar').style.display = 'none';
}}
</script>
<!-- End Floating Signup Bar -->"""

    def save_form(self, filename: str, form_type: str = 'inline', config: Dict = None) -> Path:
        """Save form to file."""
        generators = {
            'inline': self.generate_inline_form,
            'popup': self.generate_popup_form,
            'floating': self.generate_floating_bar
        }
        
        generator = generators.get(form_type, self.generate_inline_form)
        html = generator(config)
        
        filepath = self.output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return filepath

    def generate_all_forms(self, config: Dict = None) -> List[Path]:
        """Generate all form types."""
        paths = []
        
        paths.append(self.save_form('inline_form.html', 'inline', config))
        paths.append(self.save_form('popup_form.html', 'popup', config))
        paths.append(self.save_form('floating_bar.html', 'floating', config))
        
        return paths


if __name__ == '__main__':
    import sys

    generator = EmailFormGenerator()

    print("=" * 60)
    print("Email Form Generator")
    print("=" * 60)

    if len(sys.argv) < 2:
        print("\nUsage: python email_forms.py <type> [filename]")
        print("\nTypes: inline, popup, floating, all")
        print("\nExamples:")
        print("  python email_forms.py inline")
        print("  python email_forms.py popup subscribe.html")
        print("  python email_forms.py all")
        sys.exit(0)

    form_type = sys.argv[1]
    filename = sys.argv[2] if len(sys.argv) > 2 else f'{form_type}_form.html'

    config = {
        'brand_color': '#667eea',
        'title': 'Subscribe to Our Newsletter',
        'description': 'Get the latest updates and exclusive offers',
        'button_text': 'Subscribe',
        'placeholder': 'Enter your email'
    }

    if form_type == 'all':
        paths = generator.generate_all_forms(config)
        print("\n✓ Generated all forms:")
        for path in paths:
            print(f"  - {path}")
    else:
        path = generator.save_form(filename, form_type, config)
        print(f"\n✓ Generated {form_type} form: {path}")
