"""
Realistic Email Generator Module
Generate emails following real-world registration patterns
Based on common user registration trends
"""

import random
import string
from typing import List, Dict, Tuple
from datetime import datetime


class RealisticEmailGenerator:
    """
    Generate realistic emails based on actual user registration patterns
    
    Patterns observed in real registrations:
    1. firstname.lastname@domain.com (25%)
    2. firstname_lastname@domain.com (15%)
    3. firstnamelastname@domain.com (10%)
    4. firstname123@domain.com (20%)
    5. firstname.lastname123@domain.com (10%)
    6. f.lastname@domain.com (5%)
    7. firstname_l@domain.com (5%)
    8. username123@domain.com (10%)
    """
    
    def __init__(self):
        # Common first names (international)
        self.first_names = [
            # English names
            'john', 'james', 'robert', 'michael', 'william', 'david', 'richard', 'joseph',
            'thomas', 'charles', 'mary', 'patricia', 'jennifer', 'linda', 'elizabeth',
            'barbara', 'susan', 'jessica', 'sarah', 'karen', 'nancy', 'lisa', 'betty',
            'dorothy', 'sandra', 'ashley', 'kimberly', 'emily', 'donna', 'michelle',
            
            # Vietnamese names (romanized)
            'nguyen', 'tran', 'le', 'pham', 'hoang', 'huynh', 'phan', 'vu', 'dang', 'bui',
            'do', 'ho', 'ngo', 'duong', 'ly', 'minh', 'anh', 'linh', 'hoa', 'lan',
            'mai', 'thu', 'hang', 'huong', 'thao', 'duc', 'long', 'nam', 'tuan', 'hai',
            
            # Asian names
            'chen', 'wang', 'li', 'zhang', 'liu', 'yang', 'huang', 'zhao', 'wu', 'zhou',
            'tanaka', 'suzuki', 'takahashi', 'watanabe', 'ito', 'yamamoto', 'nakamura',
            'kim', 'lee', 'park', 'choi', 'jung', 'kang', 'cho', 'yoon', 'jang',
            
            # Other common names
            'ahmed', 'ali', 'omar', 'fatima', 'aisha', 'mohammed', 'hassan', 'hussein',
            'maria', 'jose', 'antonio', 'juan', 'luis', 'carlos', 'pedro', 'manuel',
            'ana', 'carmen', 'laura', 'rosa', 'sofia', 'elena', 'paula'
        ]
        
        # Common last names
        self.last_names = [
            'smith', 'johnson', 'williams', 'brown', 'jones', 'garcia', 'miller', 'davis',
            'rodriguez', 'martinez', 'hernandez', 'lopez', 'gonzalez', 'wilson', 'anderson',
            'thomas', 'taylor', 'moore', 'jackson', 'martin', 'lee', 'thompson', 'white',
            'harris', 'sanchez', 'clark', 'ramirez', 'lewis', 'robinson', 'walker',
            'nguyen', 'tran', 'le', 'pham', 'hoang', 'vu', 'dang', 'bui', 'do', 'ho',
            'chen', 'wang', 'li', 'zhang', 'liu', 'yang', 'kim', 'park', 'choi',
            'kumar', 'singh', 'patel', 'sharma', 'gupta', 'khan', 'ali', 'ahmed'
        ]
        
        # Common username words
        self.username_words = [
            'cool', 'super', 'pro', 'master', 'king', 'queen', 'star', 'hero', 'legend',
            'ninja', 'dragon', 'tiger', 'wolf', 'eagle', 'phoenix', 'shadow', 'ghost',
            'dark', 'blue', 'red', 'black', 'white', 'golden', 'silver', 'diamond',
            'tech', 'dev', 'code', 'hack', 'game', 'play', 'fast', 'speed', 'power',
            'smart', 'genius', 'brain', 'mind', 'soul', 'heart', 'true', 'real', 'best'
        ]
        
        # Popular domains
        self.popular_domains = [
            'gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com',
            'icloud.com', 'protonmail.com', 'aol.com', 'mail.com',
            'zoho.com', 'yandex.com', 'gmx.com', 'tutanota.com'
        ]
        
        # Pattern weights (probability distribution)
        self.pattern_weights = {
            'firstname.lastname': 0.25,
            'firstname_lastname': 0.15,
            'firstnamelastname': 0.10,
            'firstname_numbers': 0.20,
            'firstname.lastname_numbers': 0.10,
            'initial.lastname': 0.05,
            'firstname_initial': 0.05,
            'username_numbers': 0.10
        }
    
    def generate_year_suffix(self) -> str:
        """Generate realistic year suffix (birth years)"""
        # Common birth years for users (ages 18-50)
        current_year = datetime.now().year
        year_choices = [
            str(y)[-2:] for y in range(current_year - 50, current_year - 18)
        ]
        return random.choice(year_choices)
    
    def generate_number_suffix(self, style: str = 'random') -> str:
        """Generate realistic number suffix"""
        if style == 'year':
            return self.generate_year_suffix()
        elif style == 'birth_year':
            return str(random.randint(1970, 2006))
        elif style == 'short':
            return str(random.randint(1, 999))
        elif style == 'date':
            return f"{random.randint(1, 31):02d}{random.randint(1, 12):02d}"
        else:  # random
            length = random.choice([2, 3, 4])
            return ''.join(random.choices(string.digits, k=length))
    
    def generate_pattern_email(self, pattern: str, domain: str) -> str:
        """Generate email based on specific pattern"""
        first = random.choice(self.first_names)
        last = random.choice(self.last_names)
        username = random.choice(self.username_words)
        
        if pattern == 'firstname.lastname':
            local = f"{first}.{last}"
        
        elif pattern == 'firstname_lastname':
            local = f"{first}_{last}"
        
        elif pattern == 'firstnamelastname':
            local = f"{first}{last}"
        
        elif pattern == 'firstname_numbers':
            numbers = self.generate_number_suffix('random')
            local = f"{first}{numbers}"
        
        elif pattern == 'firstname.lastname_numbers':
            numbers = self.generate_number_suffix('short')
            local = f"{first}.{last}{numbers}"
        
        elif pattern == 'initial.lastname':
            initial = first[0]
            local = f"{initial}.{last}"
        
        elif pattern == 'firstname_initial':
            initial = last[0]
            local = f"{first}_{initial}"
        
        elif pattern == 'username_numbers':
            numbers = self.generate_number_suffix('random')
            local = f"{username}{numbers}"
        
        else:
            local = f"{first}.{last}"
        
        return f"{local}@{domain}"
    
    def generate_realistic_emails(
        self,
        count: int,
        domains: List[str] = None,
        patterns: Dict[str, float] = None,
        include_stats: bool = True
    ) -> Dict:
        """
        Generate realistic emails following actual user patterns
        
        Args:
            count: Number of emails to generate
            domains: List of domains (if None, uses popular domains)
            patterns: Custom pattern weights (if None, uses defaults)
            include_stats: Include generation statistics
        
        Returns:
            Dictionary with emails and statistics
        """
        if domains is None:
            domains = self.popular_domains
        
        if patterns is None:
            patterns = self.pattern_weights
        
        emails = []
        pattern_stats = {p: 0 for p in patterns.keys()}
        domain_stats = {d: 0 for d in domains}
        
        # Get pattern choices based on weights
        pattern_list = list(patterns.keys())
        weights = list(patterns.values())
        
        for _ in range(count):
            # Select pattern based on weights
            pattern = random.choices(pattern_list, weights=weights, k=1)[0]
            pattern_stats[pattern] += 1
            
            # Select domain randomly
            domain = random.choice(domains)
            domain_stats[domain] += 1
            
            # Generate email
            email = self.generate_pattern_email(pattern, domain)
            emails.append(email)
        
        result = {
            'success': True,
            'count': len(emails),
            'emails': emails,
            'timestamp': datetime.now().isoformat()
        }
        
        if include_stats:
            result['statistics'] = {
                'pattern_distribution': pattern_stats,
                'domain_distribution': domain_stats,
                'patterns_used': len([p for p, c in pattern_stats.items() if c > 0]),
                'domains_used': len([d for d, c in domain_stats.items() if c > 0])
            }
        
        return result
    
    def generate_themed_emails(
        self,
        theme: str,
        count: int,
        domains: List[str] = None
    ) -> Dict:
        """
        Generate emails based on specific theme
        
        Themes:
            - professional: firstname.lastname pattern
            - casual: username_numbers pattern
            - social: firstname_numbers pattern
            - gaming: username_numbers with gaming words
            - business: firstname.initial, initial.lastname
        """
        if domains is None:
            domains = self.popular_domains
        
        theme_patterns = {
            'professional': {
                'firstname.lastname': 0.60,
                'firstname.lastname_numbers': 0.25,
                'initial.lastname': 0.15
            },
            'casual': {
                'firstname_numbers': 0.40,
                'username_numbers': 0.35,
                'firstnamelastname': 0.25
            },
            'social': {
                'firstname_numbers': 0.50,
                'firstname_lastname': 0.30,
                'username_numbers': 0.20
            },
            'gaming': {
                'username_numbers': 0.70,
                'firstname_numbers': 0.20,
                'firstnamelastname': 0.10
            },
            'business': {
                'firstname.lastname': 0.50,
                'initial.lastname': 0.30,
                'firstname_initial': 0.20
            }
        }
        
        selected_patterns = theme_patterns.get(theme, self.pattern_weights)
        
        return self.generate_realistic_emails(
            count=count,
            domains=domains,
            patterns=selected_patterns,
            include_stats=True
        )
    
    def generate_bulk_with_variety(
        self,
        total: int,
        domains: List[str] = None,
        variety_level: str = 'medium'
    ) -> Dict:
        """
        Generate bulk emails with controlled variety
        
        variety_level:
            - low: 3-4 patterns only
            - medium: 5-6 patterns (default)
            - high: all 8 patterns
        """
        if domains is None:
            domains = self.popular_domains
        
        if variety_level == 'low':
            patterns = {
                'firstname.lastname': 0.40,
                'firstname_numbers': 0.35,
                'firstname_lastname': 0.25
            }
        elif variety_level == 'high':
            patterns = self.pattern_weights
        else:  # medium
            patterns = {
                'firstname.lastname': 0.30,
                'firstname_lastname': 0.20,
                'firstname_numbers': 0.25,
                'firstname.lastname_numbers': 0.15,
                'username_numbers': 0.10
            }
        
        return self.generate_realistic_emails(
            count=total,
            domains=domains,
            patterns=patterns,
            include_stats=True
        )
    
    def get_pattern_examples(self) -> Dict[str, List[str]]:
        """Get example emails for each pattern"""
        examples = {}
        
        for pattern in self.pattern_weights.keys():
            pattern_examples = []
            for _ in range(3):
                email = self.generate_pattern_email(
                    pattern,
                    random.choice(self.popular_domains[:3])
                )
                pattern_examples.append(email)
            examples[pattern] = pattern_examples
        
        return examples
    
    def get_available_options(self) -> Dict:
        """Get all available generation options"""
        return {
            'patterns': list(self.pattern_weights.keys()),
            'pattern_weights': self.pattern_weights,
            'themes': ['professional', 'casual', 'social', 'gaming', 'business'],
            'variety_levels': ['low', 'medium', 'high'],
            'popular_domains': self.popular_domains,
            'name_count': {
                'first_names': len(self.first_names),
                'last_names': len(self.last_names),
                'username_words': len(self.username_words)
            }
        }
