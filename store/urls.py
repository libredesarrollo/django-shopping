from django.urls import path

from .views import BookIndex, BookShow, PaymentBookView, StripeView, PaymentSuccessView
# from . import views

urlpatterns = [
    # listado y detalle
    path('book', BookIndex.as_view(), name='s.b.index'),
    path('<slug:slug>', BookShow.as_view(), name='s.b.show'),
    # pagar un producto
    path('payment/<str:order_id>/<int:book_id>/<str:type>', PaymentBookView.as_view(), name='s.payment'),
    # path('payment/stripe/create-checkout-session/', views.create_checkout_session, name='s.create_checkout_session'),
    # path('payment/stripe/check-payment/<str:session_id>/', views.check_payment, name='s.check_payment'),
    # crease session ID Stripe
    path('payment/stripe/create-checkout-session/', StripeView.as_view(), name='s.create_checkout_session'),
    # Pantallas de pago exito, error, cancelado    
    path('payment/success/<int:payment_id>', PaymentSuccessView.as_view(), name='s.payment.success'),
]