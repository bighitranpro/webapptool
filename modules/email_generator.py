"""
Email Generator Module
Advanced email generation with customizable parameters matching UI screenshot
"""

import random
import string
from typing import List, Dict
from datetime import datetime


class EmailGenerator:
    """Advanced email generator with multiple configuration options"""
    
    def __init__(self):
        self.email_types = {
            'random': 'Random Email',
            'name_based': 'Name Based',
            'number_based': 'Number Based',
            'mixed': 'Mixed Format'
        }
        
        self.character_types = {
            'lowercase': 'Chữ thường (a-z)',
            'uppercase': 'Chữ hoa (A-Z)',
            'mixed': 'Hỗn hợp (A-Z, a-z)',
            'alphanumeric': 'Chữ và số'
        }
        
        self.number_types = {
            'prefix': 'Số đầu',
            'suffix': 'Số cuối',
            'middle': 'Số giữa',
            'random_position': 'Vị trí ngẫu nhiên',
            'no_numbers': 'Không có số'
        }
        
        self.common_domains = [
            'gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com',
            'icloud.com', 'protonmail.com', 'mail.com', 'aol.com'
        ]
    
    def generate_character_set(self, char_type: str) -> str:
        """Generate character set based on type"""
        if char_type == 'lowercase':
            return string.ascii_lowercase
        elif char_type == 'uppercase':
            return string.ascii_uppercase
        elif char_type == 'mixed':
            return string.ascii_letters
        elif char_type == 'alphanumeric':
            return string.ascii_letters + string.digits
        else:
            return string.ascii_lowercase
    
    def generate_number_part(self, number_type: str, length: int = 4) -> str:
        """Generate number part based on type"""
        if number_type == 'no_numbers':
            return ''
        return ''.join(random.choices(string.digits, k=length))
    
    def generate_local_part(self, text: str, char_type: str, number_type: str, 
                           length_min: int = 8, length_max: int = 15) -> str:
        """Generate local part of email"""
        charset = self.generate_character_set(char_type)
        
        # Base text processing
        if text:
            base = text.lower().replace(' ', '')
        else:
            base_length = random.randint(length_min, length_max)
            base = ''.join(random.choices(charset, k=base_length))
        
        # Add numbers based on type
        if number_type == 'prefix':
            numbers = self.generate_number_part(number_type)
            local = numbers + base
        elif number_type == 'suffix':
            numbers = self.generate_number_part(number_type)
            local = base + numbers
        elif number_type == 'middle':
            numbers = self.generate_number_part(number_type)
            mid_point = len(base) // 2
            local = base[:mid_point] + numbers + base[mid_point:]
        elif number_type == 'random_position':
            numbers = self.generate_number_part(number_type)
            position = random.randint(0, len(base))
            local = base[:position] + numbers + base[position:]
        else:
            local = base
        
        # Apply character type transformation
        if char_type == 'uppercase':
            local = local.upper()
        elif char_type == 'mixed':
            local = ''.join(c.upper() if random.random() > 0.5 else c.lower() 
                          for c in local)
        
        return local
    
    def generate_emails(self, email_type: str, text: str, total: int, 
                       domain: str, char_type: str, number_type: str) -> Dict:
        """
        Generate emails based on parameters
        
        Args:
            email_type: Type of email generation
            text: Base text for generation
            total: Number of emails to generate
            domain: Email domain
            char_type: Character type (lowercase, uppercase, mixed, alphanumeric)
            number_type: Number position type
        
        Returns:
            Dict with generated emails and statistics
        """
        generated_emails = []
        
        # Validate domain
        if not domain:
            domain = random.choice(self.common_domains)
        
        # Ensure domain doesn't have @ symbol
        domain = domain.replace('@', '')
        
        for i in range(total):
            try:
                local_part = self.generate_local_part(
                    text, char_type, number_type
                )
                
                email = f"{local_part}@{domain}"
                generated_emails.append(email)
                
            except Exception as e:
                print(f"Error generating email {i+1}: {e}")
                continue
        
        return {
            'success': True,
            'total_requested': total,
            'total_generated': len(generated_emails),
            'emails': generated_emails,
            'parameters': {
                'email_type': email_type,
                'text': text,
                'domain': domain,
                'char_type': char_type,
                'number_type': number_type
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def generate_with_pattern(self, pattern: str, count: int, domain: str) -> List[str]:
        """
        Generate emails with specific pattern
        
        Pattern syntax:
            {l} - lowercase letter
            {u} - uppercase letter
            {d} - digit
            {n} - name from provided text
        """
        emails = []
        
        for _ in range(count):
            local = pattern
            local = local.replace('{l}', random.choice(string.ascii_lowercase))
            local = local.replace('{u}', random.choice(string.ascii_uppercase))
            local = local.replace('{d}', random.choice(string.digits))
            
            emails.append(f"{local}@{domain}")
        
        return emails
    
    def get_available_options(self) -> Dict:
        """Get all available generation options"""
        return {
            'email_types': self.email_types,
            'character_types': self.character_types,
            'number_types': self.number_types,
            'common_domains': self.common_domains
        }
