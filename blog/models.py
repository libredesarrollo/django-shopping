from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from django.utils import timezone

from django.db import models

# Create your models here.
import os
def upload_to_path(instance, filename):
   # Usamos el campo `path` del modelo para definir la carpeta
   return os.path.join('posts', instance.path, filename)

class Category(models.Model):
    title = models.CharField(max_length=500)
    slug = models.SlugField(max_length=500)

    def __str__(self):
        return self.title

class Post(models.Model):

    LANGUAGE_CHOICES = [
        ('english', 'English'),
        ('spanish', 'Spanish'),
        ]
    
    POSTED_CHOICES = [
        ('yes', 'Yes'),
        ('not', 'Not'),
        ]

    title = models.CharField(max_length=250, unique=True)
    slug = models.SlugField(max_length=250, unique=True)
    # date = models.DateField(auto_now_add=True)
    date = models.DateField(default=timezone.now)
    path = models.CharField(max_length=255, null=True, blank=True)
    # image = models.FileField(upload_to='posts/', null=True, blank=True)
    image = models.FileField(upload_to=upload_to_path, null=True, blank=True)
    content = models.TextField()
    description = models.CharField(max_length=500)
    posted = models.CharField(max_length=3, choices=POSTED_CHOICES, default='not')
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default='spanish')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='posts')

    # images = GenericRelation('djangoshopping.gallery.Image')
    # images = GenericRelation('store.Image')
    tags = GenericRelation('Taggable')

    def __str__(self):
        return self.title
    

    

# TAGS
class Tag(models.Model):
    title = models.CharField(max_length=500)
    slug = models.SlugField(max_length=500)

    def __str__(self):
        return self.title

    
class Taggable(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name='taggables')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        unique_together = ('tag', 'content_type', 'object_id')