from django.urls import path

from .views import BookIndex, BookShow, PaymentView

urlpatterns = [
    path('book', BookIndex.as_view(), name='s.b.index'),
    path('<slug:slug>', BookShow.as_view(), name='s.b.show'),
    path('payment/<str:order_id>/<int:book_id>/', PaymentView.as_view(), name='s.payment'),
]