"""
Email Generator - Tạo danh sách email giống người dùng thực tế
"""
import random
import string

# Danh sách họ tên phổ biến tại Việt Nam và các nước
VIETNAMESE_NAMES = {
    'first_names': ['nguyen', 'tran', 'le', 'pham', 'hoang', 'phan', 'vu', 'vo', 'dang', 'bui', 
                    'do', 'ngo', 'duong', 'ly', 'truong', 'cao', 'mai', 'luong', 'ha', 'ta'],
    'middle_names': ['van', 'thi', 'duc', 'minh', 'thanh', 'kim', 'hong', 'anh', 'thu', 'huu'],
    'last_names': ['anh', 'binh', 'cuong', 'dung', 'hai', 'hoa', 'hung', 'linh', 'long', 'mai',
                   'nam', 'phuong', 'quan', 'son', 'tuan', 'uyen', 'vy', 'xuan', 'yen', 'minh']
}

INTERNATIONAL_NAMES = {
    'first_names': ['john', 'david', 'michael', 'james', 'robert', 'william', 'richard', 'thomas',
                    'mary', 'patricia', 'jennifer', 'linda', 'elizabeth', 'barbara', 'susan'],
    'last_names': ['smith', 'johnson', 'williams', 'brown', 'jones', 'garcia', 'miller', 'davis',
                   'rodriguez', 'martinez', 'hernandez', 'lopez', 'gonzalez', 'wilson', 'anderson']
}

DOMAINS = [
    'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'icloud.com',
    'protonmail.com', 'aol.com', 'zoho.com', 'mail.com', 'gmx.com'
]


def generate_vietnamese_email():
    """Tạo email kiểu Việt Nam"""
    first = random.choice(VIETNAMESE_NAMES['first_names'])
    middle = random.choice(VIETNAMESE_NAMES['middle_names'])
    last = random.choice(VIETNAMESE_NAMES['last_names'])
    
    # Các pattern phổ biến
    patterns = [
        f"{first}{middle}{last}",
        f"{first}{last}",
        f"{first}.{middle}.{last}",
        f"{first}.{last}",
        f"{first}{middle}{last}{random.randint(1980, 2005)}",
        f"{first}.{last}{random.randint(1980, 2005)}",
    ]
    
    username = random.choice(patterns)
    domain = random.choice(DOMAINS)
    
    return f"{username}@{domain}"


def generate_international_email():
    """Tạo email kiểu quốc tế"""
    first = random.choice(INTERNATIONAL_NAMES['first_names'])
    last = random.choice(INTERNATIONAL_NAMES['last_names'])
    
    patterns = [
        f"{first}{last}",
        f"{first}.{last}",
        f"{first}_{last}",
        f"{first}{last}{random.randint(1980, 2005)}",
        f"{first}.{last}{random.randint(80, 99)}",
        f"{first[0]}{last}",
    ]
    
    username = random.choice(patterns)
    domain = random.choice(DOMAINS)
    
    return f"{username}@{domain}"


def generate_random_email():
    """Tạo email ngẫu nhiên hoàn toàn"""
    length = random.randint(6, 12)
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    domain = random.choice(DOMAINS)
    
    return f"{username}@{domain}"


def generate_emails(count=10, mix_ratio=0.7):
    """
    Tạo danh sách email
    
    Args:
        count: Số lượng email cần tạo
        mix_ratio: Tỷ lệ email Việt Nam (0.7 = 70% VN, 30% quốc tế)
    
    Returns:
        List of email addresses
    """
    emails = []
    vietnamese_count = int(count * mix_ratio)
    international_count = count - vietnamese_count
    
    # Tạo email Việt Nam
    for _ in range(vietnamese_count):
        email = generate_vietnamese_email()
        if email not in emails:  # Tránh trùng lặp
            emails.append(email)
    
    # Tạo email quốc tế
    for _ in range(international_count):
        email = generate_international_email()
        if email not in emails:
            emails.append(email)
    
    # Nếu còn thiếu do trùng lặp, tạo thêm random
    while len(emails) < count:
        email = generate_random_email()
        if email not in emails:
            emails.append(email)
    
    return emails


def get_email_info(email):
    """
    Phân tích thông tin từ email
    
    Returns:
        dict: {'username': str, 'domain': str, 'likely_origin': str}
    """
    try:
        username, domain = email.split('@')
        
        # Dự đoán nguồn gốc dựa trên pattern tên
        likely_origin = 'Unknown'
        username_lower = username.lower()
        
        # Check Vietnamese patterns
        vn_keywords = ['nguyen', 'tran', 'le', 'pham', 'van', 'thi', 'duc', 'minh']
        if any(keyword in username_lower for keyword in vn_keywords):
            likely_origin = 'Vietnam'
        elif any(name in username_lower for name in INTERNATIONAL_NAMES['first_names']):
            likely_origin = 'International'
        
        return {
            'username': username,
            'domain': domain,
            'likely_origin': likely_origin
        }
    except:
        return {
            'username': '',
            'domain': '',
            'likely_origin': 'Unknown'
        }


if __name__ == '__main__':
    # Test
    print("=== Testing Email Generator ===\n")
    
    print("10 Vietnamese-style emails:")
    for email in generate_emails(10, mix_ratio=1.0):
        info = get_email_info(email)
        print(f"  {email} -> {info['likely_origin']}")
    
    print("\n10 International-style emails:")
    for email in generate_emails(10, mix_ratio=0.0):
        info = get_email_info(email)
        print(f"  {email} -> {info['likely_origin']}")
    
    print("\n10 Mixed emails (70% VN, 30% Intl):")
    for email in generate_emails(10, mix_ratio=0.7):
        info = get_email_info(email)
        print(f"  {email} -> {info['likely_origin']}")
