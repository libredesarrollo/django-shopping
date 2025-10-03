from django.contrib import admin
from django import forms

from django.contrib.contenttypes.admin import GenericTabularInline

from .models import Category, Tag, Post, Taggable

from store.admin import BlockAdminDemo

class CategoryAdmin(BlockAdminDemo):
    list_display = ('id', 'title')
    prepopulated_fields = {'slug': ('title',) }

admin.site.register(Category, CategoryAdmin)

class TagAdmin(BlockAdminDemo):
    list_display = ('id', 'title')
    prepopulated_fields = {'slug': ('title',) }

admin.site.register(Tag, TagAdmin)

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        # fields = ('title','slug','category', 'path','content','description','posted','language','date')
        fields = ('title','slug','category', 'path','content','description','posted','language','date','image')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 10, 'cols': 80}),
        }

class TaggableInline(GenericTabularInline):
    model = Taggable
    extra = 1

@admin.register(Post)
class PostAdmin(BlockAdminDemo):
    prepopulated_fields = {'slug': ('title',) }
    inlines = [TaggableInline]
    form = PostForm
    # list_display = ('id', 'title','category')
    # fields = ('title','slug','category', 'path','content','description','posted','language','date')

 
