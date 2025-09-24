from django.views.generic import ListView, DetailView
from django.conf import settings

from django.db.models import Q
from django.utils.dateparse import parse_date
from django.utils.translation import gettext_lazy as _

from blog.models import Category, Tag
from ..models import Book

from .generic import ProductShowAbstractView

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

# Detalle del libro    
class BookShow(ProductShowAbstractView):
    model=Book
    context_object_name='book'
    template_name='store/book/show.html'
    slug_field = 'slug'            
    slug_url_kwarg = 'slug'   

# class BookShow(DetailView):
#     model=Book
#     context_object_name='book'
#     template_name='store/book/show.html'
#     slug_field = 'slug'            
#     slug_url_kwarg = 'slug'   

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         book = self.object  # Obtienes la instancia del book
#         book.price_offert = f"{book.price_offert:.2f}"   # Para evitar errores en 'es' al definir flotantes con ,
#         context['paypal_client_id'] = settings.PAYPAL_CLIENT_ID     
#         context['stripe_key'] = settings.STRIPE_KEY     
#         return context