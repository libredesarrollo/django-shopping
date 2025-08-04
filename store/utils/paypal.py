from django.conf import settings

class PaymentPaypalClient:
    def __init__(self):
        # Usar configuración desde settings.py
        env = settings.PAYPAL_PRODUCTION
        self.base_url = (
            'https://api-m.sandbox.paypal.com'
            if env
            else 'https://api-m.paypal.com'
        )
        self.client_id = settings.PAYPAL_CLIENT_ID
        self.secret = settings.PAYPAL_SECRET
        
    def __str__(self):
        return f"PayPalClient(base_url={self.base_url}, client_id={self.client_id})"