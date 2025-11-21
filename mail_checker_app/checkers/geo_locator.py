"""
Geo Locator - Dự đoán quốc gia người dùng dựa trên họ tên và domain email
"""
from typing import Dict, List


class GeoLocator:
    """Phân tích và dự đoán quốc gia từ email"""
    
    # Database các từ khóa theo quốc gia
    COUNTRY_KEYWORDS = {
        'Vietnam': {
            'names': ['nguyen', 'tran', 'le', 'pham', 'hoang', 'phan', 'vu', 'vo', 'dang', 'bui',
                     'do', 'ngo', 'duong', 'ly', 'truong', 'van', 'thi', 'duc', 'minh', 'thanh',
                     'hung', 'hai', 'hoa', 'cuong', 'dung', 'linh', 'anh', 'thao', 'mai', 'lan'],
            'domains': ['vn', '.vn'],
            'score_weight': 1.0
        },
        'USA': {
            'names': ['john', 'michael', 'david', 'james', 'robert', 'william', 'richard', 'thomas',
                     'charles', 'joseph', 'mary', 'patricia', 'jennifer', 'linda', 'elizabeth',
                     'barbara', 'susan', 'jessica', 'sarah', 'karen', 'smith', 'johnson', 'williams'],
            'domains': ['us', '.us', 'yahoo.com', 'aol.com'],
            'score_weight': 0.9
        },
        'China': {
            'names': ['wang', 'li', 'zhang', 'liu', 'chen', 'yang', 'huang', 'zhao', 'wu', 'zhou',
                     'xu', 'sun', 'ma', 'zhu', 'hu', 'guo', 'he', 'gao', 'lin', 'wei'],
            'domains': ['cn', '.cn', 'qq.com', '163.com', '126.com', 'sina.com'],
            'score_weight': 1.0
        },
        'India': {
            'names': ['kumar', 'singh', 'sharma', 'patel', 'gupta', 'reddy', 'verma', 'krishna',
                     'raj', 'ramesh', 'mahesh', 'suresh', 'rajesh', 'arun', 'vijay', 'ravi',
                     'priya', 'deepa', 'lakshmi', 'sita'],
            'domains': ['in', '.in', 'rediffmail.com'],
            'score_weight': 0.95
        },
        'Japan': {
            'names': ['tanaka', 'suzuki', 'takahashi', 'watanabe', 'sato', 'yamamoto', 'nakamura',
                     'kobayashi', 'kato', 'yoshida', 'yamada', 'sasaki', 'yamaguchi', 'matsumoto',
                     'hiroshi', 'yuki', 'akira', 'kenji'],
            'domains': ['jp', '.jp', 'yahoo.co.jp', 'docomo.ne.jp'],
            'score_weight': 1.0
        },
        'Korea': {
            'names': ['kim', 'lee', 'park', 'choi', 'jung', 'kang', 'cho', 'yoon', 'jang', 'lim',
                     'han', 'oh', 'seo', 'shin', 'kwon', 'hwang', 'ahn', 'song', 'hong', 'min'],
            'domains': ['kr', '.kr', 'naver.com', 'daum.net'],
            'score_weight': 1.0
        },
        'Thailand': {
            'names': ['somchai', 'somsak', 'surasak', 'pongpat', 'thana', 'wichai', 'anon',
                     'natthawut', 'kritsada', 'preecha', 'siriporn', 'suda', 'wannee'],
            'domains': ['th', '.th'],
            'score_weight': 0.95
        },
        'Philippines': {
            'names': ['santos', 'reyes', 'cruz', 'bautista', 'garcia', 'mendoza', 'rodriguez',
                     'fernando', 'francisco', 'jose', 'maria', 'juan', 'angel', 'carlo'],
            'domains': ['ph', '.ph'],
            'score_weight': 0.9
        },
        'UK': {
            'names': ['smith', 'jones', 'taylor', 'brown', 'davies', 'evans', 'wilson', 'thomas',
                     'roberts', 'wright', 'walker', 'robinson', 'thompson', 'white', 'harry'],
            'domains': ['uk', 'co.uk', '.uk'],
            'score_weight': 0.85
        },
        'Brazil': {
            'names': ['silva', 'santos', 'oliveira', 'souza', 'rodrigues', 'ferreira', 'alves',
                     'pereira', 'lima', 'gomes', 'costa', 'jose', 'joao', 'maria', 'ana'],
            'domains': ['br', '.br', 'uol.com.br', 'bol.com.br'],
            'score_weight': 0.9
        },
        'Mexico': {
            'names': ['garcia', 'rodriguez', 'martinez', 'hernandez', 'lopez', 'gonzalez', 'perez',
                     'sanchez', 'ramirez', 'torres', 'flores', 'rivera', 'gomez', 'diaz', 'cruz'],
            'domains': ['mx', '.mx'],
            'score_weight': 0.9
        }
    }
    
    # Common international domains (không chỉ định quốc gia cụ thể)
    NEUTRAL_DOMAINS = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'icloud.com',
                       'protonmail.com', 'mail.com', 'gmx.com', 'zoho.com', 'yandex.com']
    
    def __init__(self):
        pass
    
    def analyze_email(self, email: str) -> Dict:
        """
        Phân tích email và dự đoán quốc gia
        
        Returns:
            dict: {
                'email': str,
                'country': str,
                'confidence': float (0.0-1.0),
                'scores': dict of country scores,
                'username': str,
                'domain': str
            }
        """
        result = {
            'email': email,
            'country': 'Unknown',
            'confidence': 0.0,
            'scores': {},
            'username': '',
            'domain': ''
        }
        
        try:
            username, domain = email.split('@')
            result['username'] = username
            result['domain'] = domain
            
            username_lower = username.lower()
            domain_lower = domain.lower()
            
            # Calculate scores for each country
            country_scores = {}
            
            for country, data in self.COUNTRY_KEYWORDS.items():
                score = 0.0
                matches = 0
                
                # Check username against name keywords
                for keyword in data['names']:
                    if keyword in username_lower:
                        score += 1.0
                        matches += 1
                
                # Check domain
                for domain_keyword in data['domains']:
                    if domain_keyword in domain_lower:
                        score += 2.0  # Domain có trọng số cao hơn
                        matches += 1
                
                # Apply weight
                if matches > 0:
                    score = score * data['score_weight']
                    country_scores[country] = score
            
            result['scores'] = country_scores
            
            # Find country with highest score
            if country_scores:
                best_country = max(country_scores.items(), key=lambda x: x[1])
                result['country'] = best_country[0]
                
                # Calculate confidence (normalize score)
                max_possible_score = 5.0  # Tối đa có thể đạt được
                result['confidence'] = min(best_country[1] / max_possible_score, 1.0)
            else:
                # Nếu không match được gì, dự đoán dựa trên domain
                if domain_lower in self.NEUTRAL_DOMAINS:
                    result['country'] = 'International'
                    result['confidence'] = 0.3
                else:
                    result['country'] = 'Unknown'
                    result['confidence'] = 0.1
        
        except:
            result['country'] = 'Invalid'
            result['confidence'] = 0.0
        
        return result
    
    def analyze_bulk(self, emails: List[str]) -> List[Dict]:
        """Phân tích nhiều email"""
        return [self.analyze_email(email) for email in emails]
    
    def get_country_stats(self, results: List[Dict]) -> Dict:
        """
        Thống kê phân bố quốc gia
        
        Returns:
            dict: {country: count}
        """
        stats = {}
        for result in results:
            country = result['country']
            stats[country] = stats.get(country, 0) + 1
        return stats


def predict_country(email: str) -> Dict:
    """Helper function để predict 1 email"""
    locator = GeoLocator()
    return locator.analyze_email(email)


def predict_countries(emails: List[str]) -> List[Dict]:
    """Helper function để predict nhiều email"""
    locator = GeoLocator()
    return locator.analyze_bulk(emails)


if __name__ == '__main__':
    # Test
    print("=== Testing Geo Locator ===\n")
    
    test_emails = [
        'nguyenvananh1992@gmail.com',
        'tranminh@yahoo.com',
        'john.smith@gmail.com',
        'wangwei@163.com',
        'kumar.sharma@gmail.com',
        'tanaka@yahoo.co.jp',
        'kimlee@naver.com',
        'garcia@gmail.com',
        'silva@uol.com.br',
        'randomuser123@gmail.com'
    ]
    
    locator = GeoLocator()
    
    print("Testing country prediction:\n")
    for email in test_emails:
        result = locator.analyze_email(email)
        print(f"{email:<40} -> {result['country']:<20} (confidence: {result['confidence']:.2f})")
        if result['scores']:
            print(f"  Top scores: {dict(sorted(result['scores'].items(), key=lambda x: x[1], reverse=True)[:3])}")
        print()
    
    # Test bulk analysis
    print("\n=== Bulk Analysis Stats ===")
    results = locator.analyze_bulk(test_emails)
    stats = locator.get_country_stats(results)
    for country, count in sorted(stats.items(), key=lambda x: x[1], reverse=True):
        print(f"{country:<20}: {count} emails")
