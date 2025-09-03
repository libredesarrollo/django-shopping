
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

from django.contrib.contenttypes.models import ContentType

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
    
# Procesa la compra de un Producto/Libro
class PaymentBookView(LoginRequiredMixin, View, BasePayment):
    def __init__(self):
        # super().__init__()
        BasePayment.__init__(self)
        
    def _redirect_or_json(self, request, url_name, **kwargs):
        url = reverse(url_name, kwargs=kwargs)
        if request.headers.get("Content-Type") == "application/json":
            return JsonResponse({"redirect": url})
        return redirect(url, **kwargs)
    
    def get(self, request, order_id:str, book_id:int, type:str):
        return self._process(request, order_id, book_id, type)
    
    def post(self, request, order_id:str, book_id:int, type:str):
        return self._process(request, order_id, book_id, type) 
    
    def _process(self, request, order_id:str, book_id:int, type:str):
        #TODO revisar que NO compre el mismo producto 2 veces
     
        # si la ordenID en la URL no es valida, lo busca en el request, caso Stripe   
        # http://127.0.0.1:8000/store/payment/orderID/2/stripe?order_id=cs_test_a***pR
        if order_id == 'orderID':
            order_id = request.GET.get('order_id', '')
            if not order_id:
                return self._redirect_or_json(request, "s.payment.error", message_error=_("Not Order Found"))
     
        # procesamos la orden
        response = self.process_order(order_id, type)

        # Error en la orden
        if response == False:
            return self._redirect_or_json(request, "s.payment.error", message_error=self.message_error)
        
        #usuario auth
        user = request.user 
        
        # buscamos el producto
        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            return self._redirect_or_json(request, "s.payment.error", message_error=_("Not Book Found"))

        # creamos el producto si todo esta ok
        payment = Payment.objects.create(
            user=user,
            type=self.type,  
            coupon=None,  
            orderId=order_id,
            price=self.price,
            trace=self.trace,  
            content_type=ContentType.objects.get_for_model(book),
            object_id=book.id
        )

        return self._redirect_or_json(request, "s.payment.success", payment_id=payment.id)
    
# Procesa la compra de un Producto
class PaymentProductView(LoginRequiredMixin, View, BasePayment):
    def __init__(self):
        BasePayment.__init__(self)
        
    def _redirect_or_json(self, request, url_name, **kwargs):
        url = reverse(url_name, kwargs=kwargs)
        if request.headers.get("Content-Type") == "application/json":
            return JsonResponse({"redirect": url})
        return redirect(url, **kwargs)
    
    def get(self, request, order_id:str, product_id:int, type:str):
        return self._process(request, order_id, product_id, type)
    
    def post(self, request, order_id:str, product_id:int, type:str):
        return self._process(request, order_id, product_id, type) 
    
    def _process(self, request, order_id:str, product_id:int, type:str):
     
        # si la ordenID en la URL no es valida, lo busca en el request, caso Stripe   
        # http://127.0.0.1:8000/store/payment/orderID/2/stripe?order_id=cs_test_a***pR
        if order_id == 'orderID':
            order_id = request.GET.get('order_id', '')
            if not order_id:
                return self._redirect_or_json(request, "s.payment.error", message_error=_("Not Order Found"))
     
        # procesamos la orden
        response = self.process_order(order_id, type)

        # Error en la orden
        if response == False:
            return self._redirect_or_json(request, "s.payment.error", message_error=self.message_error)
        
        #usuario auth
        user = request.user 
        
        # buscamos el producto
        product = get_object_or_404(Product, id=product_id)

        # creamos el producto si todo esta ok
        payment = Payment.objects.create(
            user=user,
            type=self.type,  
            coupon=None,  
            orderId=order_id,
            price=self.price,
            trace=self.trace,  
            content_type=ContentType.objects.get_for_model(product),
            object_id=product.id
        )

        return self._redirect_or_json(request, "s.payment.success", payment_id=payment.id)

# STRIPE Helper View
class StripeView(LoginRequiredMixin, View, BasePayment):
    def post(self, request):
        entity = request.POST.get('entity', '')
        id = request.POST.get('id', '')
        payment_url = request.POST.get('url', '')
        
        if entity == 'book':
            try:
                product = Book.objects.get(id=id)
            except Book.DoesNotExist:
                return JsonResponse({'error': _("Not Book Found")}, status=404)
            
        # ruta relativa
        relative_url = reverse('s.payment.cancel')

        # Ruta absoluta
        cancel_absolute_url = request.build_absolute_uri(relative_url)
            
        return JsonResponse({'id': self.generate_session_id(product.title, product.price, payment_url +'?order_id={CHECKOUT_SESSION_ID}', cancel_absolute_url)})

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