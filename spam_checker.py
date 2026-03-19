"""Spam Score Checker - Analyze email content for spam triggers."""
import re
from typing import List, Tuple
from pathlib import Path


class SpamChecker:
    """Check email content for spam triggers and provide a spam score."""
    
    # Spam trigger words and phrases (high risk)
    HIGH_RISK_PHRASES = [
        'free money', 'cash bonus', 'risk free', 'guaranteed income',
        'make money fast', 'earn extra cash', 'work from home',
        'million dollars', 'lottery winner', 'claim your prize',
        'act now', 'urgent', 'immediate response', 'time sensitive',
        'click here', 'apply now', 'order now', 'buy now',
        'no cost', 'no fees', 'no obligation', 'free gift',
        'congratulations', 'you have won', 'selected specially',
        'secret deal', 'hidden charges', 'cancel anytime',
        'double your income', 'financial freedom', 'passive income'
    ]
    
    # Medium risk phrases
    MEDIUM_RISK_PHRASES = [
        'special offer', 'limited time', 'exclusive deal', 'save big',
        'discount', 'sale', 'clearance', 'bargain', 'cheap',
        'best price', 'lowest price', 'price drop', 'huge savings',
        'call now', 'don\'t miss', 'last chance', 'ending soon',
        'while supplies last', 'today only', 'flash sale',
        'unsubscribe', 'remove', 'opt out', 'no longer wish'
    ]
    
    # Formatting triggers
    FORMATTING_ISSUES = [
        ('excessive_caps', re.compile(r'[A-Z]{5,}')),  # 5+ caps in a row
        ('excessive_punctuation', re.compile(r'[!?.]{3,}')),  # 3+ punctuation
        ('dollar_signs', re.compile(r'\$\d+')),  # $ amounts
        ('percent_signs', re.compile(r'\d+%')),  # percentages
        ('arrow_symbols', re.compile(r'>>>|<<<|→|←')),  # arrows
        ('currency_words', re.compile(r'\b(dollars?|bucks?|cash)\b', re.I)),
    ]
    
    # Subject line specific triggers
    SUBJECT_TRIGGERS = [
        ('all_caps_subject', lambda s: s.isupper() and len(s) > 10),
        ('excessive_punctuation_subject', lambda s: s.count('!') > 1 or s.count('?') > 1),
        ('re_subject', lambda s: s.lower().startswith('re:') and 're:' not in s.lower()[:3]),
        ('fwd_subject', lambda s: s.lower().startswith('fwd:')),
        ('emoji_heavy', lambda s: sum(1 for c in s if ord(c) > 127) > 3),
    ]
    
    def __init__(self):
        self.weights = {
            'high_risk_phrase': 10,
            'medium_risk_phrase': 5,
            'excessive_caps': 8,
            'excessive_punctuation': 6,
            'dollar_signs': 4,
            'percent_signs': 3,
            'arrow_symbols': 5,
            'currency_words': 3,
            'all_caps_subject': 10,
            'excessive_punctuation_subject': 8,
            'emoji_heavy': 5,
            'long_subject': 3,
            'short_subject': 3,
            'image_ratio': 10,
            'link_ratio': 5,
        }
    
    def check_content(self, html_content: str) -> dict:
        """
        Check HTML email content for spam triggers.
        
        Returns dict with score and issues found.
        """
        issues = []
        score = 0
        
        # Strip HTML for text analysis
        text = re.sub(r'<[^>]+>', ' ', html_content).lower()
        
        # Check high risk phrases
        for phrase in self.HIGH_RISK_PHRASES:
            if phrase.lower() in text:
                issues.append({
                    'type': 'high_risk_phrase',
                    'severity': 'high',
                    'message': f"High-risk spam phrase: '{phrase}'",
                    'score': self.weights['high_risk_phrase']
                })
                score += self.weights['high_risk_phrase']
        
        # Check medium risk phrases
        for phrase in self.MEDIUM_RISK_PHRASES:
            if phrase.lower() in text:
                issues.append({
                    'type': 'medium_risk_phrase',
                    'severity': 'medium',
                    'message': f"Medium-risk phrase: '{phrase}'",
                    'score': self.weights['medium_risk_phrase']
                })
                score += self.weights['medium_risk_phrase']
        
        # Check formatting issues
        for issue_name, pattern in self.FORMATTING_ISSUES:
            matches = pattern.findall(html_content)
            if matches:
                issues.append({
                    'type': issue_name,
                    'severity': 'medium',
                    'message': f"Formatting issue: {issue_name.replace('_', ' ').title()} ({len(matches)} found)",
                    'score': self.weights.get(issue_name, 5)
                })
                score += self.weights.get(issue_name, 5)
        
        # Check image to text ratio
        img_count = len(re.findall(r'<img[^>]*>', html_content, re.I))
        text_length = len(text)
        if img_count > 0 and text_length < 100:
            issues.append({
                'type': 'image_ratio',
                'severity': 'high',
                'message': f"Image-heavy email with little text ({img_count} images, {text_length} chars)",
                'score': self.weights['image_ratio']
            })
            score += self.weights['image_ratio']
        
        # Check link count
        link_count = len(re.findall(r'<a[^>]*href', html_content, re.I))
        if link_count > 5:
            issues.append({
                'type': 'link_ratio',
                'severity': 'medium',
                'message': f"Many links ({link_count}) - may trigger spam filters",
                'score': self.weights['link_ratio']
            })
            score += self.weights['link_ratio']
        
        return {
            'score': min(score, 100),
            'issues': issues,
            'issue_count': len(issues),
            'high_severity': sum(1 for i in issues if i['severity'] == 'high'),
            'medium_severity': sum(1 for i in issues if i['severity'] == 'medium'),
            'low_severity': sum(1 for i in issues if i['severity'] == 'low')
        }
    
    def check_subject(self, subject: str) -> dict:
        """Check subject line for spam triggers."""
        issues = []
        score = 0
        
        # Length checks
        if len(subject) > 70:
            issues.append({
                'type': 'long_subject',
                'severity': 'low',
                'message': f"Subject too long ({len(subject)} chars, recommended < 70)",
                'score': self.weights['long_subject']
            })
            score += self.weights['long_subject']
        elif len(subject) < 10:
            issues.append({
                'type': 'short_subject',
                'severity': 'low',
                'message': f"Subject very short ({len(subject)} chars)",
                'score': self.weights['short_subject']
            })
            score += self.weights['short_subject']
        
        # Check subject-specific triggers
        for trigger_name, check_func in self.SUBJECT_TRIGGERS:
            if check_func(subject):
                issues.append({
                    'type': trigger_name,
                    'severity': 'medium',
                    'message': f"Subject trigger: {trigger_name.replace('_', ' ').title()}",
                    'score': self.weights.get(trigger_name, 5)
                })
                score += self.weights.get(trigger_name, 5)
        
        # Check for spam phrases in subject
        subject_lower = subject.lower()
        for phrase in self.HIGH_RISK_PHRASES[:10]:  # Top 10 only
            if phrase in subject_lower:
                issues.append({
                    'type': 'high_risk_phrase',
                    'severity': 'high',
                    'message': f"Spam phrase in subject: '{phrase}'",
                    'score': self.weights['high_risk_phrase']
                })
                score += self.weights['high_risk_phrase']
        
        return {
            'score': min(score, 100),
            'issues': issues,
            'issue_count': len(issues)
        }
    
    def check_full(self, subject: str, html_content: str) -> dict:
        """
        Perform full spam check on subject and content.
        
        Returns comprehensive report with recommendations.
        """
        subject_result = self.check_subject(subject)
        content_result = self.check_content(html_content)
        
        total_score = min(subject_result['score'] + content_result['score'], 100)
        
        # Determine rating
        if total_score < 20:
            rating = 'GOOD'
            recommendation = "Your email looks good! Low spam risk."
        elif total_score < 40:
            rating = 'FAIR'
            recommendation = "Some improvements could reduce spam risk."
        elif total_score < 60:
            rating = 'POOR'
            recommendation = "Consider revising to avoid spam filters."
        else:
            rating = 'HIGH RISK'
            recommendation = "High likelihood of being marked as spam. Revise recommended."
        
        return {
            'total_score': total_score,
            'rating': rating,
            'recommendation': recommendation,
            'subject_score': subject_result['score'],
            'subject_issues': subject_result['issues'],
            'content_score': content_result['score'],
            'content_issues': content_result['issues'],
            'total_issues': subject_result['issue_count'] + content_result['issue_count'],
            'high_severity': content_result['high_severity'],
            'medium_severity': content_result['medium_severity'] + subject_result['issue_count']
        }
    
    def get_recommendations(self, result: dict) -> List[str]:
        """Generate specific recommendations based on spam check results."""
        recommendations = []
        
        for issue in result.get('subject_issues', []) + result.get('content_issues', []):
            if issue['type'] == 'high_risk_phrase':
                recommendations.append("Replace spam-trigger phrases with neutral alternatives")
            elif issue['type'] == 'all_caps_subject':
                recommendations.append("Use sentence case instead of ALL CAPS in subject")
            elif issue['type'] == 'excessive_punctuation':
                recommendations.append("Reduce excessive punctuation (!!!, ???)")
            elif issue['type'] == 'image_ratio':
                recommendations.append("Add more text content relative to images")
            elif issue['type'] == 'link_ratio':
                recommendations.append("Reduce the number of links")
            elif issue['type'] == 'long_subject':
                recommendations.append("Shorten subject line to under 70 characters")
            elif issue['type'] == 'emoji_heavy':
                recommendations.append("Reduce emoji usage in subject line")
        
        # Remove duplicates
        return list(dict.fromkeys(recommendations))


def check_spam(subject: str, html_file: Path) -> dict:
    """Convenience function to check spam score."""
    checker = SpamChecker()
    
    if not html_file.exists():
        return {'error': f'File not found: {html_file}'}
    
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    return checker.check_full(subject, html_content)


if __name__ == '__main__':
    import sys
    
    print("=" * 60)
    print("Spam Score Checker")
    print("=" * 60)
    
    # Demo with sample content
    sample_subject = "🔥 URGENT!!! FREE MONEY - ACT NOW!!!"
    sample_content = """
    <html>
    <body>
        <h1>CONGRATULATIONS!!!</h1>
        <p>You have been SELECTED to receive FREE MONEY!</p>
        <p>Click here to CLAIM YOUR PRIZE now!</p>
        <p>Make money fast with our GUARANTEED INCOME system!</p>
        <a href="#">Click Here</a>
        <a href="#">Order Now</a>
        <a href="#">Act Now</a>
        <img src="promo1.jpg">
        <img src="promo2.jpg">
        <img src="promo3.jpg">
    </body>
    </html>
    """
    
    checker = SpamChecker()
    result = checker.check_full(sample_subject, sample_content)
    
    print(f"\nSubject: {sample_subject}")
    print(f"\n{'='*60}")
    print(f"SPAM SCORE: {result['total_score']}/100")
    print(f"RATING: {result['rating']}")
    print(f"\n{result['recommendation']}")
    print(f"\n{'='*60}")
    print(f"Subject Issues: {result['subject_score']} points")
    print(f"Content Issues: {result['content_score']} points")
    print(f"Total Issues: {result['total_issues']}")
    print(f"High Severity: {result['high_severity']}")
    print(f"Medium Severity: {result['medium_severity']}")
    
    print("\n--- Issues Found ---")
    for issue in result['subject_issues'] + result['content_issues']:
        print(f"  [{issue['severity'].upper()}] {issue['message']} (+{issue['score']} pts)")
    
    print("\n--- Recommendations ---")
    for rec in checker.get_recommendations(result):
        print(f"  • {rec}")
    
    print(f"\n{'='*60}\n")
    
    # Check template file if provided
    if len(sys.argv) > 1:
        template_dir = Path(__file__).parent / 'templates'
        template_name = sys.argv[1]
        
        subject_file = template_dir / f"{template_name}_subject.txt"
        html_file = template_dir / f"{template_name}.html"
        
        if subject_file.exists() and html_file.exists():
            with open(subject_file, 'r') as f:
                subject = f.read().strip()
            
            result = check_spam(subject, html_file)
            
            print(f"\nTemplate: {template_name}")
            print(f"Subject: {subject}")
            print(f"Spam Score: {result.get('total_score', 'N/A')}/100")
            print(f"Rating: {result.get('rating', 'N/A')}")
