
from django.conf import settings

import requests

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
    
    def process_order_paypal(self, order_id:str) -> bool:   
        try:
            access_token = self.get_access_token()
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}"
            }
            
            payload = {
                "application_context": {
                    "return_url": "http://djangoshopping.test/paypal",
                    "cancel_url": "http://djangoshopping.test/paypal/cancel"
                }
                # "application_context": {
                #     "return_url": "<URL-RETURN>",
                #     "cancel_url": "<URL-CANCEL>"
                # }
            }
            response = requests.post(
                f"{self.base_url}/v2/checkout/orders/{order_id}/capture",
                headers=headers,
                json=payload
            )
            data = response.json()

            if data.get("status") == "COMPLETED":
                self.status = "COMPLETED"
                self.idAPI = order_id
                self.type = "paypal"
                self.trace = data
                self.price = data.get("purchase_units", [{}])[0].get("payments", {}).get("captures", [{}])[0].get("amount", {}).get("value")
            
            return True
        except Exception as e:
            return False
            # return {"error": str(e)}

    def get_access_token(self) -> str:
        url = f"{self.base_url}/v1/oauth2/token"
        auth = (self.client_id, self.secret)
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {
            "grant_type": "client_credentials"
        }
        
        response = requests.post(url, headers=headers, auth=auth, data=data)
        response.raise_for_status()
        
        return response.json().get("access_token")
    
class BasePayment(PaymentPaypalClient):
    def process_order(self, order_id:str, type:str) -> bool:

        if type == 'paypal':
            # Paypal
            self.process_order_paypal(order_id)
        elif type == 'stripe':
            # Stripe
            # self.stripe_check_payment(orderId)
            pass
        
        return True