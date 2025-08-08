from django.views.generic import ListView, DetailView
from django.conf import settings
from django.views import View
from django.http import JsonResponse

from django.db.models import Q
from django.utils.dateparse import parse_date

from blog.models import Category, Tag
from .models import Book, Payment
from .utils.paypal import PaymentPaypalClient

from django.contrib.contenttypes.models import ContentType

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
    
# PAYPAL
class PaymentView(View, PaymentPaypalClient):
   
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        env = settings.PAYPAL_PRODUCTION
        self.base_url = (
            'https://api-m.sandbox.paypal.com'
            if env
            else 'https://api-m.paypal.com'
        )
        self.client_id = settings.PAYPAL_CLIENT_ID
        self.secret = settings.PAYPAL_SECRET

    def post(self, request, order_id, book_id):
        response = self.process_order(order_id)
        
        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            return JsonResponse({"error": _("Not Book Found")}, status=404)
        
        user = request.user 
        
        if self.status == "COMPLETED":
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
        
        return JsonResponse(response)


    
# class PaymentView(View):
   
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
        
#         env = settings.PAYPAL_PRODUCTION
#         self.base_url = (
#             'https://api-m.sandbox.paypal.com'
#             if env
#             else 'https://api-m.paypal.com'
#         )
#         self.client_id = settings.PAYPAL_CLIENT_ID
#         self.secret = settings.PAYPAL_SECRET

#     def post(self, request, order_id, book_id):
#        return JsonResponse(self.process_order(order_id))

#     def process_order(self, order_id):   
#         try:
#             access_token = self.get_access_token()
#             print(f"Access Token: {access_token}")
#             headers = {
#                 "Content-Type": "application/json",
#                 "Authorization": f"Bearer {access_token}"
#             }
#             payload = {
#                 "application_context": {
#                     "return_url": "http://djangoshopping.test/paypal",
#                     "cancel_url": "http://djangoshopping.test/paypal/cancel"
#                 }
#                 # "application_context": {
#                 #     "return_url": "<URL-RETURN>",
#                 #     "cancel_url": "<URL-CANCEL>"
#                 # }
#             }
#             response = requests.post(
#                 f"{self.base_url}/v2/checkout/orders/{order_id}/capture",
#                 headers=headers,
#                 json=payload
#             )
#             return response.json()
#         except Exception as e:
#             return {"error": str(e)}

#     def get_access_token(self):
#         url = f"{self.base_url}/v1/oauth2/token"
#         auth = (self.client_id, self.secret)
#         headers = {
#             "Accept": "application/json",
#             "Content-Type": "application/x-www-form-urlencoded"
#         }
#         data = {
#             "grant_type": "client_credentials"
#         }
#         response = requests.post(url, headers=headers, auth=auth, data=data)
#         response.raise_for_status()
#         return response.json().get("access_token")