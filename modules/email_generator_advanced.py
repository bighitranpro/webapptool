"""
Advanced Email Generator Module
RFC 5322 Compliant with Locale Awareness
Support Vietnamese and English locales with persona modes
"""

import random
import re
import json
from typing import List, Dict, Optional, Generator
from dataclasses import dataclass, asdict
from datetime import datetime
import unicodedata


@dataclass
class EmailGenerationConfig:
    """Configuration for email generation"""
    locale: str = 'vi'  # 'vi' or 'en'
    persona: str = 'personal'  # 'business', 'personal', 'casual'
    count: int = 1
    domains: List[str] = None
    number_probability: float = 0.6
    year_probability: float = 0.3
    year_range: tuple = (1980, 2005)
    dedup: bool = True
    seed: Optional[int] = None
    
    def __post_init__(self):
        if self.domains is None:
            self.domains = ['gmail.com', 'yahoo.com', 'outlook.com']


class EmailGeneratorAdvanced:
    """Advanced email generator with RFC 5322 compliance"""
    
    # Vietnamese name data
    VIETNAMESE_FIRST_NAMES = [
        'Anh', 'Bình', 'Cường', 'Dũng', 'Đức', 'Hải', 'Hiếu', 'Hùng', 'Khánh', 'Linh',
        'Long', 'Minh', 'Nam', 'Phong', 'Quân', 'Quang', 'Sơn', 'Thành', 'Tiến', 'Trung',
        'Tùng', 'Tuấn', 'Việt', 'Vũ', 'Hoàng', 'Hương', 'Lan', 'Mai', 'Nga', 'Ngọc',
        'Nhung', 'Phương', 'Thảo', 'Thư', 'Trang', 'Trinh', 'Vy', 'Yến', 'Tú', 'Thắng'
    ]
    
    VIETNAMESE_LAST_NAMES = [
        'Nguyễn', 'Trần', 'Lê', 'Phạm', 'Hoàng', 'Huỳnh', 'Phan', 'Vũ', 'Võ', 'Đặng',
        'Bùi', 'Đỗ', 'Hồ', 'Ngô', 'Dương', 'Lý', 'Đinh', 'Trương', 'Lương', 'Đào'
    ]
    
    # English name data
    ENGLISH_FIRST_NAMES = [
        'James', 'John', 'Robert', 'Michael', 'William', 'David', 'Richard', 'Joseph',
        'Thomas', 'Charles', 'Daniel', 'Matthew', 'Anthony', 'Mark', 'Donald', 'Steven',
        'Paul', 'Andrew', 'Joshua', 'Kenneth', 'Kevin', 'Brian', 'George', 'Edward',
        'Mary', 'Patricia', 'Jennifer', 'Linda', 'Barbara', 'Elizabeth'
    ]
    
    ENGLISH_LAST_NAMES = [
        'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
        'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Wilson', 'Anderson', 'Thomas',
        'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'Thompson', 'White', 'Harris'
    ]
    
    # RFC 5322 email regex pattern
    RFC5322_PATTERN = r'^[a-zA-Z0-9][a-zA-Z0-9._%+-]{0,63}@[a-zA-Z0-9][a-zA-Z0-9.-]{0,253}\.[a-zA-Z]{2,}$'
    
    def __init__(self, config: EmailGenerationConfig = None):
        self.config = config or EmailGenerationConfig()
        if self.config.seed is not None:
            random.seed(self.config.seed)
        
        self.generated_emails = set() if self.config.dedup else None
    
    @staticmethod
    def remove_vietnamese_accents(text: str) -> str:
        """Remove Vietnamese accents for email-safe strings"""
        # Vietnamese accent mappings
        vietnamese_map = {
            'à': 'a', 'á': 'a', 'ả': 'a', 'ã': 'a', 'ạ': 'a',
            'ă': 'a', 'ằ': 'a', 'ắ': 'a', 'ẳ': 'a', 'ẵ': 'a', 'ặ': 'a',
            'â': 'a', 'ầ': 'a', 'ấ': 'a', 'ẩ': 'a', 'ẫ': 'a', 'ậ': 'a',
            'đ': 'd',
            'è': 'e', 'é': 'e', 'ẻ': 'e', 'ẽ': 'e', 'ẹ': 'e',
            'ê': 'e', 'ề': 'e', 'ế': 'e', 'ể': 'e', 'ễ': 'e', 'ệ': 'e',
            'ì': 'i', 'í': 'i', 'ỉ': 'i', 'ĩ': 'i', 'ị': 'i',
            'ò': 'o', 'ó': 'o', 'ỏ': 'o', 'õ': 'o', 'ọ': 'o',
            'ô': 'o', 'ồ': 'o', 'ố': 'o', 'ổ': 'o', 'ỗ': 'o', 'ộ': 'o',
            'ơ': 'o', 'ờ': 'o', 'ớ': 'o', 'ở': 'o', 'ỡ': 'o', 'ợ': 'o',
            'ù': 'u', 'ú': 'u', 'ủ': 'u', 'ũ': 'u', 'ụ': 'u',
            'ư': 'u', 'ừ': 'u', 'ứ': 'u', 'ử': 'u', 'ữ': 'u', 'ự': 'u',
            'ỳ': 'y', 'ý': 'y', 'ỷ': 'y', 'ỹ': 'y', 'ỵ': 'y',
        }
        
        result = []
        for char in text.lower():
            result.append(vietnamese_map.get(char, char))
        
        return ''.join(result)
    
    def validate_rfc5322(self, email: str) -> bool:
        """Validate email against RFC 5322"""
        if not email or len(email) > 254:
            return False
        
        # Check basic pattern
        if not re.match(self.RFC5322_PATTERN, email):
            return False
        
        # Split local and domain parts
        parts = email.rsplit('@', 1)
        if len(parts) != 2:
            return False
        
        local, domain = parts
        
        # Check local part (max 64 chars)
        if len(local) > 64 or len(local) == 0:
            return False
        
        # Check domain part (max 253 chars)
        if len(domain) > 253 or len(domain) == 0:
            return False
        
        # No consecutive dots
        if '..' in email:
            return False
        
        # No leading/trailing dots
        if local.startswith('.') or local.endswith('.'):
            return False
        
        return True
    
    def generate_vietnamese_email(self, persona: str = 'personal') -> str:
        """Generate a Vietnamese email address"""
        first_name = random.choice(self.VIETNAMESE_FIRST_NAMES)
        last_name = random.choice(self.VIETNAMESE_LAST_NAMES)
        
        # Remove accents
        first = self.remove_vietnamese_accents(first_name)
        last = self.remove_vietnamese_accents(last_name)
        
        # Generate base patterns based on persona
        if persona == 'business':
            patterns = [
                f"{first}.{last}",
                f"{last}.{first}",
                f"{first}{last}",
            ]
        elif persona == 'casual':
            patterns = [
                f"{first}_{last}",
                f"{first}{last}",
                f"{last}{first}",
            ]
        else:  # personal
            patterns = [
                f"{first}.{last}",
                f"{first}{last}",
                f"{last}.{first}",
            ]
        
        base = random.choice(patterns)
        
        # Add numbers or years based on probability
        if random.random() < self.config.number_probability:
            if random.random() < self.config.year_probability:
                year = random.randint(self.config.year_range[0], self.config.year_range[1])
                base += str(year)
            else:
                base += str(random.randint(1, 999))
        
        domain = random.choice(self.config.domains)
        email = f"{base}@{domain}"
        
        return email.lower()
    
    def generate_english_email(self, persona: str = 'personal') -> str:
        """Generate an English email address"""
        first_name = random.choice(self.ENGLISH_FIRST_NAMES)
        last_name = random.choice(self.ENGLISH_LAST_NAMES)
        
        first = first_name.lower()
        last = last_name.lower()
        
        # Generate base patterns based on persona
        if persona == 'business':
            patterns = [
                f"{first}.{last}",
                f"{first[0]}{last}",
                f"{first}{last[0]}",
            ]
        elif persona == 'casual':
            patterns = [
                f"{first}_{last}",
                f"{first}{random.randint(1, 99)}",
                f"{last}{first}",
            ]
        else:  # personal
            patterns = [
                f"{first}.{last}",
                f"{first}{last}",
                f"{first}_{last}",
            ]
        
        base = random.choice(patterns)
        
        # Add numbers or years
        if random.random() < self.config.number_probability:
            if random.random() < self.config.year_probability:
                year = random.randint(self.config.year_range[0], self.config.year_range[1])
                base += str(year)
            else:
                base += str(random.randint(1, 999))
        
        domain = random.choice(self.config.domains)
        email = f"{base}@{domain}"
        
        return email.lower()
    
    def generate_single(self) -> Dict:
        """Generate a single email with metadata"""
        # Determine locale (80% Vietnamese if vi, 20% English)
        if self.config.locale == 'vi':
            locale = 'vi' if random.random() < 0.8 else 'en'
        else:
            locale = 'en'
        
        # Generate email based on locale
        max_attempts = 10
        for _ in range(max_attempts):
            if locale == 'vi':
                email = self.generate_vietnamese_email(self.config.persona)
            else:
                email = self.generate_english_email(self.config.persona)
            
            # Validate RFC 5322
            if not self.validate_rfc5322(email):
                continue
            
            # Check deduplication
            if self.config.dedup:
                if email not in self.generated_emails:
                    self.generated_emails.add(email)
                    break
            else:
                break
        else:
            # Fallback if max attempts reached
            email = f"user{random.randint(100000, 999999)}@{random.choice(self.config.domains)}"
        
        return {
            'email': email,
            'locale': locale,
            'persona': self.config.persona,
            'domain': email.split('@')[1] if '@' in email else None,
            'generated_at': datetime.now().isoformat(),
            'is_valid': self.validate_rfc5322(email)
        }
    
    def generate_batch(self, count: int = None) -> List[Dict]:
        """Generate multiple emails"""
        count = count or self.config.count
        emails = []
        
        for _ in range(count):
            emails.append(self.generate_single())
        
        return emails
    
    def generate_batch_stream(self, count: int = None) -> Generator[Dict, None, None]:
        """Generate emails as a stream (memory efficient for large batches)"""
        count = count or self.config.count
        
        for _ in range(count):
            yield self.generate_single()
    
    def get_statistics(self, emails: List[Dict]) -> Dict:
        """Get generation statistics"""
        total = len(emails)
        
        if total == 0:
            return {}
        
        vi_count = sum(1 for e in emails if e['locale'] == 'vi')
        en_count = total - vi_count
        
        domains = {}
        for email in emails:
            domain = email.get('domain')
            if domain:
                domains[domain] = domains.get(domain, 0) + 1
        
        personas = {}
        for email in emails:
            persona = email.get('persona')
            if persona:
                personas[persona] = personas.get(persona, 0) + 1
        
        valid_count = sum(1 for e in emails if e.get('is_valid'))
        
        return {
            'total': total,
            'valid': valid_count,
            'invalid': total - valid_count,
            'vietnamese': vi_count,
            'english': en_count,
            'locale_distribution': {
                'vi': f"{vi_count / total * 100:.1f}%",
                'en': f"{en_count / total * 100:.1f}%"
            },
            'domain_distribution': domains,
            'persona_distribution': personas,
            'deduplication_enabled': self.config.dedup,
            'unique_emails': len(self.generated_emails) if self.config.dedup else 'N/A'
        }


# CLI usage example
if __name__ == '__main__':
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description='Advanced Email Generator')
    parser.add_argument('--count', type=int, default=10, help='Number of emails to generate')
    parser.add_argument('--locale', choices=['vi', 'en'], default='vi', help='Locale (vi or en)')
    parser.add_argument('--persona', choices=['business', 'personal', 'casual'], default='personal')
    parser.add_argument('--seed', type=int, help='Random seed for reproducibility')
    parser.add_argument('--output', help='Output JSON file')
    
    args = parser.parse_args()
    
    config = EmailGenerationConfig(
        locale=args.locale,
        persona=args.persona,
        count=args.count,
        seed=args.seed
    )
    
    generator = EmailGeneratorAdvanced(config)
    emails = generator.generate_batch()
    
    result = {
        'config': asdict(config),
        'emails': emails,
        'statistics': generator.get_statistics(emails)
    }
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"✅ Generated {len(emails)} emails -> {args.output}")
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))
