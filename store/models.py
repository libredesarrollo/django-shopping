from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from django.db import models

from blog.models import Post

# Create your models here.

class Book(models.Model):
    
    POSTED_CHOICES = [
        ('yes', 'Yes'),
        ('not', 'Not'),
        ]

    title = models.CharField(max_length=250, unique=True)
    subtitle = models.CharField(max_length=250, unique=True)
    slug = models.SlugField(max_length=250, unique=True)
    date = models.DateField(auto_now_add=True)
    path = models.CharField(max_length=255, null=True, blank=True)
    image = models.CharField(max_length=255, null=True, blank=True)
    content = models.CharField(max_length=500)
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
    posted = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='paypal')
    coupon = models.CharField(max_length=100, null=True, blank=True)
    orderId = models.CharField(max_length=500, unique=True)
    price = models.DecimalField(max_digits=7, decimal_places=2, default=0.00)
    trace = models.CharField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)

    path = models.CharField(max_length=255, null=True, blank=True)
    image = models.CharField(max_length=255, null=True, blank=True)
    content = models.CharField(max_length=500)
    
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    paymentable = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return f"{self.user.username} - {self.orderId}"