from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from django_ckeditor_5.fields import CKEditor5Field

from django.db import models

from blog.models import Post

import os

def upload_to_path(instance, filename):

   return os.path.join('books', instance.path, filename)

class Book(models.Model):
    
    POSTED_CHOICES = [
        ('yes', 'Yes'),
        ('not', 'Not'),
        ]

    title = models.CharField(max_length=250, unique=True)
    subtitle = models.CharField(max_length=250, unique=True)
    slug = models.SlugField(max_length=250, unique=True)
    # date = models.DateField(auto_now_add=True)
    date = models.DateField(default=timezone.now)
    path = models.CharField(max_length=255, null=True, blank=True)
    # image = models.FileField(upload_to='books/', null=True, blank=True)
    image = models.FileField(upload_to=upload_to_path, null=True, blank=True)
    # content = models.TextField()
    content = CKEditor5Field('Content', config_name='default', blank=True, null=True)
    description = models.CharField(max_length=500)
    posted = models.CharField(max_length=3, choices=POSTED_CHOICES, default='not')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='books')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    page = models.PositiveIntegerField(default=0)

    price = models.DecimalField(max_digits=7, decimal_places=2, default=0.00)
    price_offert = models.DecimalField(max_digits=7, decimal_places=2, default=0.00)

    images = GenericRelation('Image')
    tags = GenericRelation('blog.Taggable')

    def __str__(self):
        return self.title

class Image(models.Model):
    path = models.CharField(max_length=255)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

class Payment(models.Model):
    
    PAYMENT_CHOICES = [
        ('paypal', 'PayPal'),
        ('stripe', 'Stripe'),
        ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='paypal')
    coupon = models.CharField(max_length=100, null=True, blank=True)
    orderId = models.CharField(max_length=500, unique=True)
    price = models.DecimalField(max_digits=7, decimal_places=2, default=0.00)
    trace = models.CharField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)
    
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    paymentable = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return f"{self.user.username} - {self.orderId}"