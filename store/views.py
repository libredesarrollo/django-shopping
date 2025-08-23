from django.views.generic import ListView, DetailView
from django.conf import settings
from django.views import View
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404

from django.db.models import Q
from django.utils.dateparse import parse_date
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

from django.shortcuts import render
from django.urls import reverse

import stripe

import json

from blog.models import Category, Tag
from .models import Book, Payment
from .utils.payment import BasePayment

from django.contrib.contenttypes.models import ContentType

stripe.api_key = settings.STRIPE_SECRET

# Listado de libros
class BookIndex(ListView):
    model = Book
    context_object_name = 'books'
    template_name = 'store/book/index.html'
    paginate_by = 15

    def get_queryset(self):
        queryset = Book.objects.filter(posted='yes').select_related('post').prefetch_related('tags')

        search = self.request.GET.get('search', '')
        category_id = self.request.GET.get('category_id')
        tag_id = self.request.GET.get('tag_id')
        language = self.request.GET.get('language')
        from_date = self.request.GET.get('from')
        to_date = self.request.GET.get('to')

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )
        # if language:
        #     queryset = queryset.filter(language=language)
        # if category_id:
        #     queryset = queryset.filter(category_id=category_id)
        
        if language:
            queryset = queryset.filter(post__language=language)
        if category_id:
            queryset = queryset.filter(post__category_id=category_id)
        
        if tag_id:
            queryset = queryset.filter(tags__id=tag_id)
        if from_date and to_date:
            from_date_parsed = parse_date(from_date)
            to_date_parsed = parse_date(to_date)
            if from_date_parsed and to_date_parsed:
                queryset = queryset.filter(date__range=(from_date_parsed, to_date_parsed))

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['tags'] = Tag.objects.all()
        context['paypal_client_id'] = settings.PAYPAL_CLIENT_ID
        
        return context
    
# Detalle del pago    
class BookShow(DetailView):
    model=Book
    context_object_name='book'
    template_name='store/book/show.html'
    slug_field = 'slug'            
    slug_url_kwarg = 'slug'   

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['paypal_client_id'] = settings.PAYPAL_CLIENT_ID     
        context['stripe_key'] = settings.STRIPE_KEY     
        return context
        
    
    
# Procesa la compra de un Producto/Libro
class PaymentBookView(LoginRequiredMixin, View, BasePayment):
    def __init__(self):
        # super().__init__()
        BasePayment.__init__(self) 
   
    def get(self, request, order_id:str, book_id:int, type:str):
        return self.process(request, order_id, book_id, type)
    
    def post(self, request, order_id:str, book_id:int, type:str):
        return self.process(request, order_id, book_id, type) 
    
    def process(self, request, order_id:str, book_id:int, type:str):
        #TODO revisar que NO compre el mismo producto 2 veces
     
        # si la ordenID en la URL no es valida, lo busca en el request, caso Stripe   
        # http://127.0.0.1:8000/store/payment/orderID/2/stripe?order_id=cs_test_a***pR
        if order_id == 'orderID':
            order_id = request.GET.get('order_id', '')
            if not order_id:
                # return redirect("s.payment.error", message_error=_("Not Order Found"))
                # return JsonResponse({"error": _("Not Order Found")}, status=404)
                if request.headers.get("Content-Type") == "application/json":
                    return JsonResponse({"redirect": reverse("s.payment.error", kwargs={"message_error": _("Not Order Found")})})
        
                return redirect("s.payment.error", message_error=_("Not Order Found"))
     
        # procesamos la orden
        response = self.process_order(order_id, type)

        # Error en la orden
        if response == False:
            # return JsonResponse({"error": self.message_error}, status=400)
            # return redirect("s.payment.error", message_error=self.message_error)
            if request.headers.get("Content-Type") == "application/json":
                return JsonResponse({"redirect": reverse("s.payment.error", kwargs={"message_error": self.message_error})})
            return redirect("s.payment.error", message_error=self.message_error)
        
        #usuario auth
        user = request.user 
        
        # buscamos el producto
        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            return JsonResponse({"error": _("Not Book Found")}, status=404)

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
            
        if request.headers.get("Content-Type") == "application/json":
            return JsonResponse({"redirect": reverse("s.payment.success", kwargs={"payment_id": payment.id})})
        
        return redirect("s.payment.success", payment_id=payment.id)

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
            
        return JsonResponse({'id': self.generate_session_id(product.title, product.price, payment_url +'?order_id={CHECKOUT_SESSION_ID}')})

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



# @csrf_exempt
# def create_checkout_session(request):

#     entity = request.POST.get('entity', '')
#     id = request.POST.get('id', '')
    
#     if entity == 'book':
#         try:
#             product = Book.objects.get(id=id)
#         except Book.DoesNotExist:
#             return JsonResponse({'error': 'Libro no encontrado'}, status=404)
#     try:
#         checkout_session = stripe.checkout.Session.create(
#             payment_method_types=['card'],
#             line_items=[
#                 {
#                     'price_data': {
#                         'currency': 'usd',
#                         'product_data': {
#                             'name': product.title,
#                         },
#                         'unit_amount': int(Decimal(product.price_offert) * 100),  # en centavos
#                     },
#                     'quantity': 1,
#                 },
#             ],
#             mode='payment',
#             success_url='http://localhost:8000/success?order_id={CHECKOUT_SESSION_ID}',
#             cancel_url='http://localhost:8000/cancel',
#         )
#         return JsonResponse({'id': checkout_session.id})
#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=400)
    
    
# def check_payment(request,session_id):
#     try:
#         # Obtener la sesión de Stripe
#         session = stripe.checkout.Session.retrieve(session_id)
#         # Revisar si el pago está completo
#         if session.payment_status == 'paid':
#             result = {
#                 'status': 'COMPLETED',
#                 'idAPI': session_id,
#                 'responseAPI': json.dumps(dict(session)),  # Convierte objeto a dict
#                 # 'responseAPI': json.loads(json.dumps(dict(session))),  # Convierte a dict para JSON
#                 'payment': 'stripe',
#                 'price': session.amount_total // 100  # Convertir de centavos a unidad
#             }

#         return JsonResponse(result)
#     except stripe.error.StripeError as e:
#         return JsonResponse({'error': str(e)}, status=400)



# class CreateCheckoutSessionView(View):
#     def get(self, request, session_id, *args, **kwargs):
#         try:
#             # Obtener la sesión de Stripe
#             session = stripe.checkout.Session.retrieve(session_id)

#             if session.payment_status == 'paid':
#                 result = {
#                     'status': 'COMPLETED',
#                     'idAPI': session_id,
#                     'responseAPI': json.dumps(dict(session)),
#                     'payment': 'stripe',
#                     'price': session.amount_total // 100
#                 }
#                 return JsonResponse(result)

#             return JsonResponse({'status': session.payment_status})
#         except stripe.error.StripeError as e:
#             return JsonResponse({'error': str(e)}, status=400)
        
#     def post(self, request, *args, **kwargs):
#         entity = request.POST.get('entity', '')
#         entity_id = request.POST.get('id', '')

#         product = None
#         if entity == 'book':
#             try:
#                 product = Book.objects.get(id=entity_id)
#             except Book.DoesNotExist:
#                 return JsonResponse({'error': 'Libro no encontrado'}, status=404)

#         try:
#             checkout_session = stripe.checkout.Session.create(
#                 payment_method_types=['card'],
#                 line_items=[
#                     {
#                         'price_data': {
#                             'currency': 'usd',
#                             'product_data': {
#                                 'name': product.title,
#                             },
#                             'unit_amount': int(Decimal(product.price_offert) * 100),  # en centavos
#                         },
#                         'quantity': 1,
#                     },
#                 ],
#                 mode='payment',
#                 success_url='http://localhost:8000/success?order_id={CHECKOUT_SESSION_ID}',
#                 cancel_url='http://localhost:8000/cancel',
#             )
#             return JsonResponse({'id': checkout_session.id})
#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=400)

