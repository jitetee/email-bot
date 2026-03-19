"""Email Preheader Generator - Generate preview text for emails."""
from pathlib import Path
import re


class PreheaderGenerator:
    """Generate email preheader text from subject and content."""

    def __init__(self):
        self.max_length = 100  # Recommended max for email clients

    def generate_from_subject(self, subject: str, method: str = 'extend') -> str:
        """
        Generate preheader from subject line.

        Args:
            subject: Email subject line
            method: Generation method (extend, question, teaser, summary)

        Returns:
            Preheader text
        """
        subject = subject.strip()

        methods = {
            'extend': self._extend_subject(subject),
            'question': self._create_question(subject),
            'teaser': self._create_teaser(subject),
            'summary': self._create_summary(subject)
        }

        return methods.get(method, self._extend_subject(subject))

    def _extend_subject(self, subject: str) -> str:
        """Extend the subject line with more details."""
        extensions = [
            f"Discover what's inside...",
            f"Your exclusive offer awaits!",
            f"Read more to find out...",
            f"Inside: Everything you need to know",
            f"Don't miss out on this opportunity",
            f"See what we have for you",
            f"Your personalized content is ready",
            f"Open to learn more",
        ]
        import random
        return f"{subject} - {random.choice(extensions)}"[:self.max_length]

    def _create_question(self, subject: str) -> str:
        """Create a question-based preheader."""
        questions = [
            "Ready to learn more?",
            "Want to see what's inside?",
            "Curious about what's new?",
            "Interested in exclusive offers?",
            "Want to be the first to know?",
        ]
        import random
        return random.choice(questions)

    def _create_teaser(self, subject: str) -> str:
        """Create a teaser preheader."""
        teasers = [
            "🎁 Something special awaits you inside...",
            "✨ You won't believe what we have for you!",
            "🔥 Hot deals just for you...",
            "💎 Exclusive content for valued subscribers...",
            "🌟 Your VIP access is ready...",
        ]
        import random
        return random.choice(teasers)[:self.max_length]

    def _create_summary(self, subject: str) -> str:
        """Create a summary-style preheader."""
        return f"In this email: Special offers, updates, and more just for you."[:self.max_length]

    def generate_from_content(self, html_content: str, max_length: int = None) -> str:
        """
        Extract preheader from HTML email content.

        Args:
            html_content: HTML email body
            max_length: Maximum length

        Returns:
            Extracted preheader text
        """
        max_length = max_length or self.max_length

        # Strip HTML tags
        text = re.sub(r'<[^>]+>', ' ', html_content)

        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove common unwanted phrases
        unwanted = [
            'view in browser',
            'unsubscribe',
            'forward',
            'subscribe',
            'email preferences'
        ]
        for phrase in unwanted:
            text = re.sub(rf'(?i){phrase}.*', '', text)

        # Get first meaningful sentence
        text = text.strip()

        # Find first sentence or chunk
        if len(text) <= max_length:
            return text

        # Try to break at word boundary
        chunk = text[:max_length]
        last_space = chunk.rfind(' ')
        if last_space > max_length - 20:
            chunk = chunk[:last_space]

        return chunk + '...'

    def generate_best_practices(self, subject: str) -> dict:
        """
        Generate multiple preheader options with best practices.

        Returns:
            Dict with options and tips
        """
        return {
            'subject': subject,
            'options': {
                'extend': self.generate_from_subject(subject, 'extend'),
                'question': self.generate_from_subject(subject, 'question'),
                'teaser': self.generate_from_subject(subject, 'teaser'),
                'summary': self.generate_from_subject(subject, 'summary')
            },
            'tips': [
                'Keep preheader under 100 characters',
                'Complement the subject line, don\'t repeat it',
                'Include a call-to-action when possible',
                'Personalize when you can',
                'Avoid "View in browser" as preheader',
                'Test how it looks in different email clients'
            ],
            'character_count': len(subject)
        }

    def validate_preheader(self, preheader: str) -> dict:
        """
        Validate preheader quality.

        Returns:
            Validation results
        """
        issues = []
        suggestions = []

        # Check length
        if len(preheader) > 130:
            issues.append(f"Too long ({len(preheader)} chars). Recommended: <100")
        elif len(preheader) < 20:
            suggestions.append("Consider making it more descriptive")

        # Check for spam triggers
        spam_words = ['free', 'buy now', 'urgent', 'act now', 'limited time']
        for word in spam_words:
            if word.lower() in preheader.lower():
                suggestions.append(f"Avoid spam trigger word: '{word}'")

        # Check for view in browser
        if 'view in browser' in preheader.lower():
            issues.append("'View in browser' will show in inbox preview")

        return {
            'preheader': preheader,
            'length': len(preheader),
            'valid': len(issues) == 0,
            'issues': issues,
            'suggestions': suggestions,
            'score': max(0, 100 - len(issues) * 20 - len(suggestions) * 10)
        }


if __name__ == '__main__':
    import sys

    generator = PreheaderGenerator()

    print("=" * 60)
    print("Email Preheader Generator")
    print("=" * 60)

    if len(sys.argv) < 2:
        print("\nUsage: python preheader.py <subject> [method]")
        print("\nExamples:")
        print('  python preheader.py "Summer Sale 50% Off"')
        print('  python preheader.py "Summer Sale" teaser')
        print('  python preheader.py "New Product Launch" validate')
        print("\nMethods: extend, question, teaser, summary, best")
        sys.exit(0)

    subject = sys.argv[1]
    method = sys.argv[2] if len(sys.argv) > 2 else 'best'

    if method == 'validate':
        # Generate and validate
        preheader = generator.generate_from_subject(subject, 'extend')
        result = generator.validate_preheader(preheader)
        
        print(f"\nSubject: {subject}")
        print(f"\nGenerated Preheader: {preheader}")
        print(f"\nValidation:")
        print(f"  Length: {result['length']} characters")
        print(f"  Score: {result['score']}/100")
        if result['issues']:
            print(f"  Issues:")
            for issue in result['issues']:
                print(f"    ✗ {issue}")
        if result['suggestions']:
            print(f"  Suggestions:")
            for sug in result['suggestions']:
                print(f"    → {sug}")

    elif method == 'best':
        result = generator.generate_best_practices(subject)
        
        print(f"\nSubject: {subject}")
        print(f"Character Count: {result['character_count']}")
        print("\nPreheader Options:")
        print("-" * 60)
        for name, text in result['options'].items():
            print(f"\n{name.upper()}:")
            print(f"  {text}")
        
        print("\n" + "=" * 60)
        print("Best Practices Tips:")
        print("=" * 60)
        for tip in result['tips']:
            print(f"  ✓ {tip}")

    else:
        preheader = generator.generate_from_subject(subject, method)
        print(f"\nSubject: {subject}")
        print(f"Method: {method}")
        print(f"\nGenerated Preheader:")
        print(f"  {preheader}")
        print(f"\nLength: {len(preheader)} characters")
