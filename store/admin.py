from django.contrib import admin
from django import forms

from django.contrib.contenttypes.admin import GenericTabularInline

from .models import Book
from blog.models import Taggable

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        # fields = ('title','slug','category', 'path','content','description','posted','language','date')
        fields = ('title','subtitle','slug','post', 'path','content','description','posted', 'date','image', 'user', 'price_offert', 'price')
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