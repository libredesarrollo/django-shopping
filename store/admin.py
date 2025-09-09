from django.contrib import admin
from django import forms

from django.contrib.contenttypes.admin import GenericTabularInline
from django.contrib.contenttypes.models import ContentType

from .models import Book, Product, ProductType, Payment
from blog.models import Taggable

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        # fields = ('title','slug','category', 'path','content','description','posted','language','date')
        fields = ('title','subtitle','slug','post', 'path','content','description','posted', 'date','image', 'user', 'price_offert', 'price', 'page')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 10, 'cols': 80}),
        }

class TaggableInline(GenericTabularInline):
    model = Taggable
    extra = 1

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',) }
    inlines = [TaggableInline]
    form = BookForm
    
    
#**** tipo producto
# producto
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ('title','subtitle','slug','post', 'path','content','description','posted','product_type', 'date','image', 'user', 'price_offert', 'price')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 10, 'cols': 80}),
        }
        
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',) }
    inlines = [TaggableInline]
    form = ProductForm
    
# tipo producto
@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
    prepopulated_fields = {'slug': ('title',) }
# admin.site.register(ProductType, ProductTypeAdmin)

#**** producto
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id','created_at', 'user', 'short_orderId','type', 'price')
    list_filter = ('user', 'type')
    search_fields = ('id', 'user__username', 'type', 'trace', 'orderId') 
    
    def short_orderId(self, obj):
        if obj.orderId:  # suponiendo que tu campo se llama trace
            return (obj.orderId[:20] + '...') if len(obj.orderId) > 20 else obj.orderId
        return ''
    short_orderId.short_description = "orderId"