from django.urls import path

from .views import BookIndex, BookShow, ProductIndex, ProductShow, PaymentBookView, PaymentProductView, StripeView, PaymentSuccessView, PaymentCancelView, PaymentErrorView, UserPaymentsView, ProductIndexByType

# from . import views

urlpatterns = [
    # listado y detalle Book
    path('book', BookIndex.as_view(), name='s.b.index'),
    path('book/<slug:slug>', BookShow.as_view(), name='s.b.show'),
    # listado y detalle Product
    # path('product/<slug:slug>', ProductShow.as_view(), name='s.p.show'),
    path('product', ProductIndex.as_view(), name='s.p.index'),
    path('product/<slug:slug>/', ProductIndexByType.as_view(), name='s.p.t.index'),
    path('product/<slug:type>/<slug:slug>', ProductShow.as_view(), name='s.p.show'),
    # path('product/<slug:type>', ProductIndex.as_view(), name='s.p.index'),
    # pagar un producto/book
    path('payment/<str:order_id>/<int:book_id>/<str:type>', PaymentBookView.as_view(), name='s.payment'),
    # pagar un producto
    path('product/payment/<str:order_id>/<int:product_id>/<str:type>', PaymentProductView.as_view(), name='s.product.payment'),
    # path('payment/stripe/create-checkout-session/', views.create_checkout_session, name='s.create_checkout_session'),
    # path('payment/stripe/check-payment/<str:session_id>/', views.check_payment, name='s.check_payment'),
    # crease session ID Stripe
    path('payment/stripe/create-checkout-session/', StripeView.as_view(), name='s.create_checkout_session'),
    # Pantallas de pago exito, error, cancelado    
    path('payment/success/<int:payment_id>', PaymentSuccessView.as_view(), name='s.payment.success'),
    path('payment/cancel/', PaymentCancelView.as_view(), name='s.payment.cancel'),
    path('payment/error/', PaymentErrorView.as_view(), name='s.payment.error'),
    path('payment/error/<str:message_error>', PaymentErrorView.as_view(), name='s.payment.error'),
    # listado de pagos del usuario
    path("user/payments/", UserPaymentsView.as_view(), name="s.payments.user"),
]