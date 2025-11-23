"""
Email Template System Module
Pre-built templates for various purposes with customization
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
import json


@dataclass
class EmailTemplate:
    """Email template definition"""
    id: str
    name: str
    description: str
    category: str
    pattern: str
    variables: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)


class EmailTemplateSystem:
    """System for managing and generating emails from templates"""
    
    def __init__(self):
        self.templates = self._init_templates()
        self.categories = {
            'business': 'Business & Professional',
            'personal': 'Personal Use',
            'testing': 'Testing & Development',
            'marketing': 'Marketing & Sales',
            'ecommerce': 'E-commerce',
            'social': 'Social Media'
        }
    
    def _init_templates(self) -> Dict[str, EmailTemplate]:
        """Initialize built-in templates"""
        templates = {}
        
        # Business Templates
        templates['business_standard'] = EmailTemplate(
            id='business_standard',
            name='Business Standard',
            description='Professional business email format',
            category='business',
            pattern='{firstname}.{lastname}@{domain}',
            variables=['firstname', 'lastname', 'domain'],
            examples=[
                'john.smith@company.com',
                'jane.doe@business.com'
            ],
            tags=['professional', 'standard', 'corporate']
        )
        
        templates['business_initial'] = EmailTemplate(
            id='business_initial',
            name='Business Initial',
            description='First initial + last name format',
            category='business',
            pattern='{first_initial}{lastname}@{domain}',
            variables=['first_initial', 'lastname', 'domain'],
            examples=[
                'jsmith@company.com',
                'jdoe@business.com'
            ],
            tags=['professional', 'concise']
        )
        
        templates['business_department'] = EmailTemplate(
            id='business_department',
            name='Business Department',
            description='Department-based email format',
            category='business',
            pattern='{firstname}.{lastname}.{department}@{domain}',
            variables=['firstname', 'lastname', 'department', 'domain'],
            examples=[
                'john.smith.sales@company.com',
                'jane.doe.marketing@business.com'
            ],
            tags=['professional', 'department', 'organized']
        )
        
        # Personal Templates
        templates['personal_casual'] = EmailTemplate(
            id='personal_casual',
            name='Personal Casual',
            description='Casual personal email with numbers',
            category='personal',
            pattern='{firstname}{numbers}@{domain}',
            variables=['firstname', 'numbers', 'domain'],
            examples=[
                'john123@gmail.com',
                'jane456@yahoo.com'
            ],
            tags=['casual', 'personal', 'simple']
        )
        
        templates['personal_underscore'] = EmailTemplate(
            id='personal_underscore',
            name='Personal Underscore',
            description='Personal email with underscore separator',
            category='personal',
            pattern='{firstname}_{lastname}@{domain}',
            variables=['firstname', 'lastname', 'domain'],
            examples=[
                'john_smith@gmail.com',
                'jane_doe@yahoo.com'
            ],
            tags=['personal', 'readable']
        )
        
        templates['personal_year'] = EmailTemplate(
            id='personal_year',
            name='Personal with Year',
            description='Personal email with birth year',
            category='personal',
            pattern='{firstname}.{lastname}{year}@{domain}',
            variables=['firstname', 'lastname', 'year', 'domain'],
            examples=[
                'john.smith1990@gmail.com',
                'jane.doe1995@yahoo.com'
            ],
            tags=['personal', 'age-based']
        )
        
        # Testing Templates
        templates['testing_random'] = EmailTemplate(
            id='testing_random',
            name='Random Testing',
            description='Random string for testing purposes',
            category='testing',
            pattern='test_{random_string}@{domain}',
            variables=['random_string', 'domain'],
            examples=[
                'test_abc123xyz@testmail.com',
                'test_def456uvw@devmail.com'
            ],
            tags=['testing', 'development', 'random']
        )
        
        templates['testing_sequential'] = EmailTemplate(
            id='testing_sequential',
            name='Sequential Testing',
            description='Sequential numbering for testing',
            category='testing',
            pattern='test{sequence}@{domain}',
            variables=['sequence', 'domain'],
            examples=[
                'test001@testmail.com',
                'test002@testmail.com'
            ],
            tags=['testing', 'sequential', 'organized']
        )
        
        # Marketing Templates
        templates['marketing_campaign'] = EmailTemplate(
            id='marketing_campaign',
            name='Marketing Campaign',
            description='Campaign-based marketing emails',
            category='marketing',
            pattern='{campaign}_{identifier}@{domain}',
            variables=['campaign', 'identifier', 'domain'],
            examples=[
                'spring_sale_001@marketing.com',
                'holiday_promo_002@campaign.com'
            ],
            tags=['marketing', 'campaign', 'tracking']
        )
        
        templates['marketing_segment'] = EmailTemplate(
            id='marketing_segment',
            name='Marketing Segment',
            description='Customer segment based emails',
            category='marketing',
            pattern='{segment}.{firstname}.{lastname}@{domain}',
            variables=['segment', 'firstname', 'lastname', 'domain'],
            examples=[
                'vip.john.smith@customer.com',
                'premium.jane.doe@client.com'
            ],
            tags=['marketing', 'segmentation', 'personalized']
        )
        
        # E-commerce Templates
        templates['ecommerce_customer'] = EmailTemplate(
            id='ecommerce_customer',
            name='E-commerce Customer',
            description='Customer account emails',
            category='ecommerce',
            pattern='customer.{id}@{domain}',
            variables=['id', 'domain'],
            examples=[
                'customer.12345@shop.com',
                'customer.67890@store.com'
            ],
            tags=['ecommerce', 'customer', 'account']
        )
        
        templates['ecommerce_vendor'] = EmailTemplate(
            id='ecommerce_vendor',
            name='E-commerce Vendor',
            description='Vendor/seller account emails',
            category='ecommerce',
            pattern='vendor.{shop_name}@{domain}',
            variables=['shop_name', 'domain'],
            examples=[
                'vendor.techstore@marketplace.com',
                'vendor.fashionshop@platform.com'
            ],
            tags=['ecommerce', 'vendor', 'business']
        )
        
        # Social Media Templates
        templates['social_username'] = EmailTemplate(
            id='social_username',
            name='Social Username',
            description='Social media style usernames',
            category='social',
            pattern='{username}@{domain}',
            variables=['username', 'domain'],
            examples=[
                'cool_user_123@social.com',
                'awesome.person@community.com'
            ],
            tags=['social', 'username', 'casual']
        )
        
        templates['social_handle'] = EmailTemplate(
            id='social_handle',
            name='Social Handle',
            description='Social media handle style',
            category='social',
            pattern='@{handle}@{domain}',
            variables=['handle', 'domain'],
            examples=[
                '@johndoe@social.com',
                '@janedoe@network.com'
            ],
            tags=['social', 'handle', 'unique']
        )
        
        # Vietnamese Templates
        templates['vietnamese_standard'] = EmailTemplate(
            id='vietnamese_standard',
            name='Vietnamese Standard',
            description='Standard Vietnamese name format (without accents)',
            category='personal',
            pattern='{ho}{ten}@{domain}',
            variables=['ho', 'ten', 'domain'],
            examples=[
                'nguyenvan@gmail.com',
                'tranthithu@yahoo.com'
            ],
            tags=['vietnamese', 'personal', 'standard']
        )
        
        templates['vietnamese_dot'] = EmailTemplate(
            id='vietnamese_dot',
            name='Vietnamese Dot Separated',
            description='Vietnamese name with dot separator',
            category='personal',
            pattern='{ten}.{ho}@{domain}',
            variables=['ten', 'ho', 'domain'],
            examples=[
                'van.nguyen@gmail.com',
                'thu.tran@yahoo.com'
            ],
            tags=['vietnamese', 'personal', 'readable']
        )
        
        templates['vietnamese_year'] = EmailTemplate(
            id='vietnamese_year',
            name='Vietnamese with Year',
            description='Vietnamese name with birth year',
            category='personal',
            pattern='{ho}{ten}{year}@{domain}',
            variables=['ho', 'ten', 'year', 'domain'],
            examples=[
                'nguyenvan1995@gmail.com',
                'tranthithu2000@yahoo.com'
            ],
            tags=['vietnamese', 'personal', 'age-based']
        )
        
        return templates
    
    def get_all_templates(self) -> List[Dict]:
        """Get all templates as list of dicts"""
        return [
            {
                'id': t.id,
                'name': t.name,
                'description': t.description,
                'category': t.category,
                'pattern': t.pattern,
                'variables': t.variables,
                'examples': t.examples,
                'tags': t.tags
            }
            for t in self.templates.values()
        ]
    
    def get_templates_by_category(self, category: str) -> List[Dict]:
        """Get templates filtered by category"""
        return [
            {
                'id': t.id,
                'name': t.name,
                'description': t.description,
                'category': t.category,
                'pattern': t.pattern,
                'variables': t.variables,
                'examples': t.examples,
                'tags': t.tags
            }
            for t in self.templates.values()
            if t.category == category
        ]
    
    def get_template(self, template_id: str) -> Optional[Dict]:
        """Get specific template by ID"""
        template = self.templates.get(template_id)
        if not template:
            return None
        
        return {
            'id': template.id,
            'name': template.name,
            'description': template.description,
            'category': template.category,
            'pattern': template.pattern,
            'variables': template.variables,
            'examples': template.examples,
            'tags': template.tags
        }
    
    def search_templates(self, query: str) -> List[Dict]:
        """Search templates by name, description, or tags"""
        query_lower = query.lower()
        results = []
        
        for template in self.templates.values():
            if (query_lower in template.name.lower() or
                query_lower in template.description.lower() or
                any(query_lower in tag.lower() for tag in template.tags)):
                
                results.append({
                    'id': template.id,
                    'name': template.name,
                    'description': template.description,
                    'category': template.category,
                    'pattern': template.pattern,
                    'variables': template.variables,
                    'examples': template.examples,
                    'tags': template.tags
                })
        
        return results
    
    def generate_from_template(self, template_id: str, 
                               variables: Dict[str, str], 
                               count: int = 1) -> Dict:
        """
        Generate emails from template with variable substitution
        
        Args:
            template_id: Template ID to use
            variables: Dict of variable values
            count: Number of emails to generate
        
        Returns:
            Dict with generated emails and metadata
        """
        template = self.templates.get(template_id)
        if not template:
            return {
                'success': False,
                'error': f'Template not found: {template_id}'
            }
        
        # Validate required variables
        missing_vars = [v for v in template.variables if v not in variables]
        if missing_vars:
            return {
                'success': False,
                'error': f'Missing required variables: {", ".join(missing_vars)}'
            }
        
        # Generate emails
        generated_emails = []
        pattern = template.pattern
        
        for i in range(count):
            email = pattern
            
            # Substitute variables
            for var_name, var_value in variables.items():
                placeholder = f'{{{var_name}}}'
                
                # Handle special cases
                if var_name == 'first_initial':
                    # Get first letter of firstname
                    firstname = variables.get('firstname', 'x')
                    email = email.replace(placeholder, firstname[0].lower())
                else:
                    email = email.replace(placeholder, str(var_value).lower())
            
            generated_emails.append(email)
        
        return {
            'success': True,
            'template_id': template_id,
            'template_name': template.name,
            'emails': generated_emails,
            'count': len(generated_emails),
            'variables_used': variables,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_categories(self) -> Dict[str, str]:
        """Get all available categories"""
        return self.categories.copy()
    
    def export_templates(self, filepath: str) -> bool:
        """Export all templates to JSON file"""
        try:
            data = {
                'version': '1.0',
                'exported_at': datetime.now().isoformat(),
                'categories': self.categories,
                'templates': self.get_all_templates()
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Export failed: {e}")
            return False
    
    def import_templates(self, filepath: str) -> bool:
        """Import templates from JSON file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Import templates
            for template_data in data.get('templates', []):
                template = EmailTemplate(**template_data)
                self.templates[template.id] = template
            
            return True
        except Exception as e:
            print(f"Import failed: {e}")
            return False


# Example usage
if __name__ == '__main__':
    system = EmailTemplateSystem()
    
    # Get all templates
    print("📧 All Templates:")
    for t in system.get_all_templates():
        print(f"  • {t['name']} ({t['category']})")
    
    print("\n🏢 Business Templates:")
    for t in system.get_templates_by_category('business'):
        print(f"  • {t['name']}: {t['pattern']}")
    
    print("\n🔍 Search 'vietnamese':")
    for t in system.search_templates('vietnamese'):
        print(f"  • {t['name']}: {t['examples'][0]}")
    
    print("\n✨ Generate from template:")
    result = system.generate_from_template(
        'business_standard',
        {'firstname': 'John', 'lastname': 'Smith', 'domain': 'company.com'},
        count=3
    )
    print(f"  Generated: {result['emails']}")
