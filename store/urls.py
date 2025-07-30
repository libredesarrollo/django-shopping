from django.urls import path

from .views import BookIndex, BookShow

urlpatterns = [
    path('book', BookIndex.as_view(), name='s.b.index'),
    path('<slug:slug>', BookShow.as_view(), name='s.b.show')
]