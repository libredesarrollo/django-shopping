from django.views.generic import ListView, DetailView
from django.conf import settings

from django.db.models import Q
from django.utils.dateparse import parse_date
from django.utils.translation import gettext_lazy as _

from blog.models import Category, Tag
from ..models import Product, ProductType, Coupon

from ..utils.coupon import UtilityCoupon

from abc import ABC


#******** Listado/Detalle de Products
class ProductIndexAbstract(ListView, ABC):
    model = Product
    context_object_name = 'products'
    template_name = 'store/product/index.html'
    paginate_by = 15

    def get_queryset(self):

        queryset = Product.objects.filter(posted='yes').select_related('post').prefetch_related('tags')

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
    
class ProductIndex(ProductIndexAbstract):
    pass

#******** Listado de Products por tipo producto     
class ProductIndexByType(ProductIndexAbstract):

    def get_queryset(self):
        queryset = super().get_queryset()
        slug = self.kwargs.get("slug")
        return queryset.filter(product_type__slug=slug)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product_type = ProductType.objects.filter(slug=self.kwargs.get("slug")).get()
        context["template_path"] = f"store/product/partials/list/{product_type.slug}.html"
        return context
    

    
# Detalle del producto    
class ProductShow(DetailView, UtilityCoupon):
    model=Product
    context_object_name='product'
    template_name='store/product/show.html'
    slug_field = 'slug'            
    slug_url_kwarg = 'slug'   
    
    def get(self, request, *args, **kwargs):
        coupon = request.GET.get('coupon')
        self.coupon = coupon

        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object  # Obtienes la instancia del producto
        
        context['paypal_client_id'] = settings.PAYPAL_CLIENT_ID     
        context['stripe_key'] = settings.STRIPE_KEY     
        context["template_path"] = f"store/product/partials/detail/{product.product_type.slug}.html"

        if self.coupon:
            self.messageCoupon = self.check_coupon(self.coupon, product.price_offert)
            context["coupon"] = self.coupon

            context["messageCoupon"] = self.messageCoupon   
        
        product.price_offert = f"{product.price_offert:.2f}"   # Para evitar errores en 'es' al definir flotantes con ,

        

        return context    
    
    def get_queryset(self):
        queryset = super().get_queryset()
        product_slug = self.kwargs.get("slug")
        type_slug = self.kwargs.get("type")
        
        return queryset.filter(
            slug=product_slug,
            product_type__slug=type_slug
        )