from django.views.generic import ListView, DetailView
from django.conf import settings
from django.views import View
from django.http import JsonResponse

from django.db.models import Q
from django.utils.dateparse import parse_date
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt

import stripe

from blog.models import Category, Tag
from .models import Book, Payment
from .utils.payment import BasePayment

from django.contrib.contenttypes.models import ContentType

stripe.api_key = settings.STRIPE_SECRET

# Create your views here.
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
    
class BookShow(DetailView):
    model=Book
    context_object_name='book'
    template_name='store/book/show.html'
    slug_field = 'slug'            
    slug_url_kwarg = 'slug'   

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['paypal_client_id'] = settings.PAYPAL_CLIENT_ID     
        return context
    
# BOOK BUY
class PaymentBookView(LoginRequiredMixin, View, BasePayment):
   
    def post(self, request, order_id:str, book_id:int, type:str):

        #TODO revisar que NO compre el mismo producto 2 veces

        # procesamos la orden
        response = self.process_order(order_id, type)
        
        # buscamos el producto
        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            return JsonResponse({"error": _("Not Book Found")}, status=404)
        
        #usuario auth
        user = request.user 
        
        # creamos el producto si todo esta ok
        if response == True:
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
        
        return JsonResponse({"status": "ok"})


@csrf_exempt
def create_checkout_session(request):
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'Producto de prueba',
                        },
                        'unit_amount': 2000,  # en centavos, $20.00
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url='http://localhost:8000/success',
            cancel_url='http://localhost:8000/cancel',
        )
        return JsonResponse({'id': checkout_session.id})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)