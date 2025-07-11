from django.db import models

# Create your models here.

class Category(models.Model):
    title = models.CharField(max_length=500)
    slug = models.SlugField(max_length=500)

    def __str__(self):
        return self.title

