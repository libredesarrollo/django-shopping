from django.contrib import admin
from django import forms

from .models import Category, Tag, Post

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')

admin.site.register(Category, CategoryAdmin)


class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')

admin.site.register(Tag, TagAdmin)


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        list_display = ('id', 'title','category')
        # fields = ('title','slug','category', 'path','content','description','posted','language','date')
        fields = ('title','slug','category', 'path','content','description','posted','language','date','image')
        # class Meta:
        # widgets = {
        #     'description': forms.Textarea(attrs={'rows': 10, 'cols': 80}),
        # }


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    form = PostForm
    # list_display = ('id', 'title','category')
    # fields = ('title','slug','category', 'path','content','description','posted','language','date')

 
