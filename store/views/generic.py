from django.views.generic import DetailView
from django.conf import settings

from django.contrib.contenttypes.models import ContentType

from ..models import Payment

from ..utils.coupon import UtilityCoupon


# clase a usar para todos los detalles de entidades comprables
class ProductShowAbstractView(DetailView, UtilityCoupon):
    
    def get(self, request, *args, **kwargs):
        self.coupon = request.GET.get('coupon')
        self.step_one = request.GET.get('step_one')
 
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object  # Obtienes la instancia del producto
        
        # claves de pago
        context['paypal_client_id'] = settings.PAYPAL_CLIENT_ID     
        context['stripe_key'] = settings.STRIPE_KEY     
        # template de detalle personalizado
        
        # indica si es el paso 1 (cupon y boton de pago) o 2 (paypal y stripe botones)
        context["step_one"] = self.step_one 

        # si hay cupon, lo procesa
        if self.coupon:
            # verifica si es valido
            self.messageCoupon = self.check_coupon(self.coupon, product.price_offert)
            context["coupon"] = self.coupon
            
            if self.messageCoupon.get('status') == 'success':
                # product.price_offert = f"{self.final_price:.2f}"   # Para evitar errores en 'es' al definir flotantes con ,
                # es valido, aplica el cupon
                product.price_offert = self.final_price 
            else:
                # no es valido, sigue en el paso 1
                context["step_one"] = None
        
            context["messageCoupon"] = self.messageCoupon
        
        if self.request.user.is_authenticated:
            context["payment"] = Payment.objects.filter(
                    user=self.request.user,
                    object_id=self.object.id,
                    content_type=ContentType.objects.get_for_model(self.object) 
                ).order_by("-created_at").first()
            
        # Para evitar errores en 'es' al definir flotantes con ,
        product.price_offert = f"{product.price_offert:.2f}"
            
        return context    