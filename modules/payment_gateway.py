"""
Payment Gateway Module
Support for Momo and VietQR payment integrations
"""

import hmac
import hashlib
import requests
import json
import qrcode
import io
import base64
from typing import Dict, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class PaymentConfig:
    """Payment gateway configuration"""
    momo_partner_code: str = ""
    momo_access_key: str = ""
    momo_secret_key: str = ""
    momo_endpoint: str = "https://test-payment.momo.vn/v2/gateway/api/create"
    momo_return_url: str = "https://your-domain.com/payment/momo/return"
    momo_notify_url: str = "https://your-domain.com/payment/momo/notify"
    
    # VietQR configuration
    bank_id: str = "970422"  # MB Bank default
    account_no: str = ""
    account_name: str = ""
    
    # VIP pricing (USD)
    vip_prices: Dict[int, float] = None
    
    def __post_init__(self):
        if self.vip_prices is None:
            self.vip_prices = {
                1: 10.0,   # VIP 1: $10
                2: 50.0,   # VIP 2: $50
                3: 200.0   # VIP 3: $200
            }


class PaymentGateway:
    """Payment gateway handler for Momo and VietQR"""
    
    def __init__(self, config: PaymentConfig = None):
        self.config = config or PaymentConfig()
    
    def create_momo_payment(
        self,
        order_id: str,
        amount: float,
        order_info: str,
        user_id: int = None,
        extra_data: str = ""
    ) -> Dict:
        """
        Create Momo payment request
        
        Args:
            order_id: Unique order ID
            amount: Payment amount in VND
            order_info: Order description
            user_id: User ID (optional)
            extra_data: Additional data (optional)
        
        Returns:
            Dict with payment URL and QR code
        """
        
        # Request data
        request_id = f"MM{datetime.now().strftime('%Y%m%d%H%M%S')}"
        amount = int(amount)  # Momo requires integer
        
        request_data = {
            "partnerCode": self.config.momo_partner_code,
            "partnerName": "BIGHI Tool MMO",
            "storeId": "BIGHITOOL",
            "requestId": request_id,
            "amount": amount,
            "orderId": order_id,
            "orderInfo": order_info,
            "redirectUrl": self.config.momo_return_url,
            "ipnUrl": self.config.momo_notify_url,
            "lang": "vi",
            "extraData": extra_data,
            "requestType": "captureWallet",
            "autoCapture": True
        }
        
        # Create signature
        raw_signature = (
            f"accessKey={self.config.momo_access_key}"
            f"&amount={amount}"
            f"&extraData={extra_data}"
            f"&ipnUrl={self.config.momo_notify_url}"
            f"&orderId={order_id}"
            f"&orderInfo={order_info}"
            f"&partnerCode={self.config.momo_partner_code}"
            f"&redirectUrl={self.config.momo_return_url}"
            f"&requestId={request_id}"
            f"&requestType=captureWallet"
        )
        
        signature = hmac.new(
            self.config.momo_secret_key.encode('utf-8'),
            raw_signature.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        request_data['signature'] = signature
        
        # Send request to Momo
        try:
            response = requests.post(
                self.config.momo_endpoint,
                json=request_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            response_data = response.json()
            
            if response_data.get('resultCode') == 0:
                return {
                    'success': True,
                    'payment_url': response_data.get('payUrl'),
                    'qr_code_url': response_data.get('qrCodeUrl'),
                    'deeplink': response_data.get('deeplink'),
                    'order_id': order_id,
                    'request_id': request_id
                }
            else:
                return {
                    'success': False,
                    'error': response_data.get('message', 'Unknown error'),
                    'result_code': response_data.get('resultCode')
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_momo_signature(self, response_data: Dict) -> bool:
        """
        Verify Momo callback signature
        
        Args:
            response_data: Response data from Momo callback
        
        Returns:
            True if signature is valid
        """
        
        received_signature = response_data.get('signature')
        if not received_signature:
            return False
        
        # Build raw signature
        raw_signature = (
            f"accessKey={self.config.momo_access_key}"
            f"&amount={response_data.get('amount')}"
            f"&extraData={response_data.get('extraData', '')}"
            f"&message={response_data.get('message')}"
            f"&orderId={response_data.get('orderId')}"
            f"&orderInfo={response_data.get('orderInfo')}"
            f"&orderType={response_data.get('orderType')}"
            f"&partnerCode={response_data.get('partnerCode')}"
            f"&payType={response_data.get('payType')}"
            f"&requestId={response_data.get('requestId')}"
            f"&responseTime={response_data.get('responseTime')}"
            f"&resultCode={response_data.get('resultCode')}"
            f"&transId={response_data.get('transId')}"
        )
        
        calculated_signature = hmac.new(
            self.config.momo_secret_key.encode('utf-8'),
            raw_signature.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(calculated_signature, received_signature)
    
    def create_vietqr_payment(
        self,
        order_id: str,
        amount: float,
        description: str
    ) -> Dict:
        """
        Create VietQR payment (bank transfer with QR code)
        
        Args:
            order_id: Unique order ID
            amount: Payment amount in VND
            description: Payment description
        
        Returns:
            Dict with QR code image
        """
        
        # VietQR API (using vietqr.io service)
        vietqr_api = "https://api.vietqr.io/v2/generate"
        
        request_data = {
            "accountNo": self.config.account_no,
            "accountName": self.config.account_name,
            "acqId": self.config.bank_id,
            "amount": int(amount),
            "addInfo": f"{description} - {order_id}",
            "format": "text",
            "template": "compact"
        }
        
        try:
            response = requests.post(
                vietqr_api,
                json=request_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            response_data = response.json()
            
            if response_data.get('code') == '00':
                qr_data = response_data['data']['qrDataURL']
                
                return {
                    'success': True,
                    'qr_code_url': qr_data,
                    'bank_id': self.config.bank_id,
                    'account_no': self.config.account_no,
                    'account_name': self.config.account_name,
                    'amount': amount,
                    'description': description,
                    'order_id': order_id
                }
            else:
                # Fallback: Generate QR code manually
                return self._generate_qr_fallback(order_id, amount, description)
                
        except Exception as e:
            # Fallback: Generate QR code manually
            return self._generate_qr_fallback(order_id, amount, description)
    
    def _generate_qr_fallback(self, order_id: str, amount: float, description: str) -> Dict:
        """Generate QR code locally as fallback"""
        
        # VietQR format
        qr_content = (
            f"{self.config.bank_id}|"
            f"{self.config.account_no}|"
            f"{self.config.account_name}|"
            f"{int(amount)}|"
            f"{description} - {order_id}"
        )
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_content)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return {
            'success': True,
            'qr_code_url': f"data:image/png;base64,{img_base64}",
            'bank_id': self.config.bank_id,
            'account_no': self.config.account_no,
            'account_name': self.config.account_name,
            'amount': amount,
            'description': description,
            'order_id': order_id,
            'note': 'QR generated locally (fallback)'
        }
    
    def calculate_vip_price(self, vip_level: int, duration_months: int = 1) -> float:
        """
        Calculate VIP subscription price with discounts
        
        Args:
            vip_level: VIP level (1, 2, or 3)
            duration_months: Subscription duration in months
        
        Returns:
            Total price in USD
        """
        
        base_price = self.config.vip_prices.get(vip_level, 0)
        
        if base_price == 0:
            return 0
        
        total = base_price * duration_months
        
        # Apply discounts
        if duration_months >= 12:
            total *= 0.8  # 20% discount for 12 months
        elif duration_months >= 6:
            total *= 0.9  # 10% discount for 6 months
        elif duration_months >= 3:
            total *= 0.95  # 5% discount for 3 months
        
        return round(total, 2)
    
    def create_vip_subscription_order(
        self,
        user_id: int,
        vip_level: int,
        duration_months: int = 1,
        payment_method: str = 'momo'
    ) -> Dict:
        """
        Create VIP subscription order
        
        Args:
            user_id: User ID
            vip_level: VIP level (1, 2, or 3)
            duration_months: Subscription duration
            payment_method: 'momo' or 'bank'
        
        Returns:
            Order details with payment information
        """
        
        price_usd = self.calculate_vip_price(vip_level, duration_months)
        
        # Convert USD to VND (approximate rate: 1 USD = 24,000 VND)
        price_vnd = int(price_usd * 24000)
        
        order_id = f"VIP{vip_level}_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        order_info = f"VIP {vip_level} - {duration_months} month(s)"
        
        if payment_method == 'momo':
            payment_result = self.create_momo_payment(
                order_id=order_id,
                amount=price_vnd,
                order_info=order_info,
                user_id=user_id,
                extra_data=json.dumps({
                    'vip_level': vip_level,
                    'duration_months': duration_months,
                    'user_id': user_id
                })
            )
        else:  # bank transfer
            payment_result = self.create_vietqr_payment(
                order_id=order_id,
                amount=price_vnd,
                description=order_info
            )
        
        return {
            'order_id': order_id,
            'user_id': user_id,
            'vip_level': vip_level,
            'duration_months': duration_months,
            'price_usd': price_usd,
            'price_vnd': price_vnd,
            'payment_method': payment_method,
            'payment_data': payment_result,
            'expires_at': (datetime.now() + timedelta(days=duration_months * 30)).isoformat()
        }


# CLI usage example
if __name__ == '__main__':
    import sys
    
    # Example configuration (use environment variables in production)
    config = PaymentConfig(
        momo_partner_code="MOMOXXX",
        momo_access_key="XXX",
        momo_secret_key="XXX",
        account_no="1234567890",
        account_name="NGUYEN VAN A"
    )
    
    gateway = PaymentGateway(config)
    
    # Test VIP pricing
    print("VIP Pricing:")
    for level in [1, 2, 3]:
        for months in [1, 3, 6, 12]:
            price = gateway.calculate_vip_price(level, months)
            print(f"  VIP {level} - {months} month(s): ${price}")
    
    # Test QR code generation (fallback)
    print("\nTesting QR code generation...")
    result = gateway.create_vietqr_payment(
        order_id="TEST123",
        amount=100000,
        description="Test payment"
    )
    
    if result['success']:
        print(f"✅ QR code generated successfully")
        print(f"   Order ID: {result['order_id']}")
        print(f"   Amount: {result['amount']} VND")
    else:
        print(f"❌ Failed: {result.get('error')}")
