
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import timedelta

from django.contrib.contenttypes.models import ContentType

from typing import TypeVar

from ..models import Coupon, ProductAbstract

class UtilityCoupon:
    
    def check_coupon(self, coupon_code, price_product):
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
        if coupon.user_id is not None or coupon.couponable is not None:
            return {
                "status": "error",
                "message": "Coupon Used"
            }

        # 4. Aplica el cupón
        self.final_price = price_product - coupon.price

        return {
            "status": "success",
            "message": "Coupon Applied",
        }
    
    T = TypeVar("T", bound=ProductAbstract)

    def mark_coupon_as_used(self, coupon_code: str, user: User, obj: T):
        coupon = Coupon.objects.get(coupon=coupon_code)
        coupon.user = user
        coupon.content_type=ContentType.objects.get_for_model(obj)
        coupon.object_id=obj.id
        coupon.save()