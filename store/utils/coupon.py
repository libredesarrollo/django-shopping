
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse

from ..models import Coupon

class UtilityCoupon:
    
    def check_coupon(self, coupon_code, priceProduct):
        # 1. Elimina cupones antiguos (más de 30 días)
        Coupon.objects.filter(created_at__lt=timezone.now() - timedelta(days=30)).delete()

        # 2. Busca el cupón
        try:
            coupon = Coupon.objects.get(coupon=coupon_code)
        except Coupon.DoesNotExist:
            return {
                "status": "error",
                "message": "Coupon Invalid"
            }

        # 3. Verifica si ya fue usado
        if coupon.user_id is not None or coupon.academy_couponable_id is not None:
            return {
                "status": "error",
                "message": "Coupon Used"
            }

        # 4. Aplica el cupón
        self.finalPrice = priceProduct - coupon.price

        return {
            "status": "success",
            "message": "Coupon Applied",
        }