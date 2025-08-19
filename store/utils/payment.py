
from django.conf import settings

import stripe
import requests

from decimal import Decimal
import json

stripe.api_key = settings.STRIPE_SECRET

class AbstractPayment:
    status: str = None
    idAPI: str = None
    type: str = None
    trace: str = None
    price: float = None
    # def __init__(self, status, idAPI, type, trace, price):
    #     self.status = status
    #     self.idAPI = idAPI
    #     self.type = type          # (paypal, stripe, etc.)
    #     self.trace = trace        # traza del pago
    #     self.price = price


# Capa 1 PayPal plataforma de pago 
class PaymentPaypalClient(AbstractPayment):
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
                self.trace = json.dumps(data)
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


# Capa 3 Pasarela de Pago Stripe
class PaymentStripeClient(AbstractPayment):
    # def __init__(self, product_title: str, product_price: float, product_id: int, success_url: str):
    #     # Detalles del producto a comprar

    #     self.product_price = product_price
    #     self.product_title = product_title
    #     self.product_id = product_id

    def generate_session_id(self, product_title: str, product_price: float, success_url: str) -> str:

        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price_data': {
                            'currency': 'usd',
                            'product_data': {
                                'name': product_title,
                            },
                            'unit_amount': int(Decimal(product_price) * 100),  # en centavos
                        },
                        'quantity': 1,
                    },
                ],
                mode='payment',
                success_url=success_url,
                cancel_url='http://localhost:8000/cancel',
            )
            return checkout_session.id
        except Exception as e:
            return str(e)

    def check_order_stripe(self, session_id: str):
        try:
            # Obtener la sesión de Stripe
            session = stripe.checkout.Session.retrieve(session_id)

            if session.payment_status == 'paid':
                self.status = 'COMPLETED'
                self.idAPI = session_id
                self.type = 'stripe'
                self.trace = json.dumps(dict(session))
                self.price = session.amount_total // 100
                # self.status = 'COMPLETED',
                # self.idAPI = session_id,
                # self.type = 'stripe',
                # self.trace = json.dumps(dict(session)),
                # self.price = session.amount_total // 100

        except stripe.error.StripeError as e:
            pass #str(e)
        
    


# Capa 2    
class BasePayment(PaymentPaypalClient, PaymentStripeClient):
    def process_order(self, order_id:str, type:str) -> bool:

        if type == 'paypal':
            # Paypal
            self.process_order_paypal(order_id)
        elif type == 'stripe':
            # Stripe
            self.check_order_stripe(order_id)
        
        return True