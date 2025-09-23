
from django.views.generic import ListView
from django.views import View
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404

from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

from django.shortcuts import render
from django.urls import reverse

from ..models import Book, Product, Payment
from ..utils.payment import BasePayment

from ..utils.coupon import UtilityCoupon

from django.contrib.contenttypes.models import ContentType

import json

# listado de pagos del usuario        
class UserPaymentsView(LoginRequiredMixin, ListView):
    model = Payment
    template_name = "store/user/payments.html"
    context_object_name = "payments"

    def get_queryset(self):
        # equivalente a: Payment::where("user_id", auth()->user()->id)->with("paymentable")->get();
        return (
            Payment.objects.filter(user=self.request.user)
            # .select_related("paymentable")  
            .order_by("-created_at")
        )
    
# Procesa el pago
class BasePaymentView(LoginRequiredMixin, View, BasePayment, UtilityCoupon):
    model = None          # el modelo (Book o Product)
    lookup_field = "id"   # campo de búsqueda (generalmente id)
    url_kwarg = None      # el parámetro en la URL (book_id, product_id)

    def __init__(self):
        BasePayment.__init__(self)

    def _redirect_or_json(self, request, url_name, **kwargs):
        url = reverse(url_name, kwargs=kwargs)
        if request.headers.get("Content-Type") == "application/json":
            return JsonResponse({"redirect": url})
        return redirect(url, **kwargs)

    def get(self, request, order_id: str, type: str, **kwargs): # parametro extra (**kwargs) que es el de <int:product_id>/<int:book_id>
        return self._process(request, order_id, type, **kwargs) 

    def post(self, request, order_id: str, type: str, **kwargs): # parametro extra (**kwargs) que es el de <int:product_id>/<int:book_id>
        return self._process(request, order_id, type, **kwargs)

    def _process(self, request, order_id: str, type: str, **kwargs):
        # si la ordenID en la URL no es valida, lo busca en el request (caso Stripe)   
        if order_id == 'orderID':
            order_id = request.GET.get('order_id', '')
            if not order_id:
                return self._redirect_or_json(request, "s.payment.error", message_error=_("Not Order Found"))
            
        # busca si ha cupon
        # por get viene de stripe
        coupon = request.GET.get('coupon')
        if not coupon:
            # por post viene de paypal
            coupon = request.POST.get('coupon') # NO HACE falta, ya que por paypal espera es application/json

        # verificamos si la peticion es de tipo json (paypal)
        if not coupon and request.content_type == 'application/json':
            try:
                body = json.loads(request.body)
                coupon = body.get('coupon')
            except (json.JSONDecodeError, AttributeError):
                coupon = None

        # procesamos la orden
        response = self.process_order(order_id, type)
        if response is False:
            return self._redirect_or_json(request, "s.payment.error", message_error=self.message_error)

        # usuario auth
        user = request.user 

        # buscamos el objeto parametro extra <int:product_id>/<int:book_id>
        pk = kwargs.get(self.url_kwarg)
        obj = get_object_or_404(self.model, **{self.lookup_field: pk})

        # creamos el payment
        payment = Payment.objects.create(
            user=user,
            type=self.type,
            coupon=coupon,
            orderId=order_id,
            price=self.price,
            trace=self.trace,
            content_type=ContentType.objects.get_for_model(obj),
            object_id=obj.id
        )

        # registramos el cupon como consumido
        if coupon:
            self.mark_coupon_as_used(coupon, user, obj)


        return self._redirect_or_json(request, "s.payment.success", payment_id=payment.id)

# Procesa la compra de un Libro
class PaymentBookView(BasePaymentView):
    model = Book
    url_kwarg = "book_id"

# Procesa la compra de un Producto
class PaymentProductView(BasePaymentView):
    model = Product
    url_kwarg = "product_id"

# STRIPE Helper View
class StripeView(LoginRequiredMixin, View, BasePayment, UtilityCoupon):
    def post(self, request):
        entity = request.POST.get('entity', '')
        id = request.POST.get('id', '')
        coupon = request.POST.get('coupon', '')
        payment_url = request.POST.get('url', '')
        
        # *** buscamos la entidad
        if entity == 'book':
            try:
                product = Book.objects.get(id=id)
            except Book.DoesNotExist:
                return JsonResponse({'error': _("Not Book Found")}, status=404)
            
        if entity == 'product':
            try:
                product = Product.objects.get(id=id)
            except Product.DoesNotExist:
                return JsonResponse({'error': _("Not Product Found")}, status=404)
            
        # ruta relativa
        relative_url = reverse('s.payment.cancel')

        # Ruta absoluta
        cancel_absolute_url = request.build_absolute_uri(relative_url)

        # *** verificamos si hay un cupon como parte de la URL
        if coupon:
             # verificamos el cupon
            messageCoupon = self.check_coupon(coupon, product.price_offert)
            if messageCoupon.get('status') == 'success':
                # es valido, aplica el cupon
                product.price_offert = self.final_price 
                # aplicamos el cupon en la URL
                payment_url = (f"{payment_url}?coupon={coupon}")+"&order_id={CHECKOUT_SESSION_ID}"
        else:
            # Generamos la URL de pago por defecto
            payment_url = payment_url +'?order_id={CHECKOUT_SESSION_ID}'
  
            
        return JsonResponse({'id': self.generate_session_id(product.title, product.price_offert, payment_url, cancel_absolute_url)})

#*** Pantallas de pago exito, error, cancelado    
class PaymentSuccessView(LoginRequiredMixin, View):
    def get(self, request, payment_id:int):
        payment = get_object_or_404(Payment, id=payment_id)

        # solamente lo puede ver el dueno del pago
        if payment.user_id != request.user.id:
            raise PermissionDenied

        return render(request, 'store/payments/success.html', {'payment': payment})
    
class PaymentCancelView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'store/payments/cancel.html')

class PaymentErrorView(LoginRequiredMixin, View):
    def get(self, request, message_error:str = ''):
        return render(request, 'store/payments/error.html', {'message_error': message_error})