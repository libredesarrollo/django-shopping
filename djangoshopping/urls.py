"""
URL configuration for djangoshopping project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from user.views import ToggleThemeView
from django.views.generic.base import RedirectView
from allauth.account.views import LoginView, LogoutView

from django.conf import settings

from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('toggle-theme/', ToggleThemeView.as_view(), name='toggle_theme'),
    path("blog/", include('blog.urls')),
    path("store/", include('store.urls')),
    path("accounts/", include('user.urls')),
    path("ckeditor5/", include('django_ckeditor_5.urls')),
    # django auth all
    # path('accounts/', include('allauth.urls')),
    path('accounts/login/', LoginView.as_view(), name='account_login'),
    path('i18n/', include('django.conf.urls.i18n')), 
    path('', RedirectView.as_view(url='/store/product')),#, permanent=True
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEMO:
    urlpatterns += [
        path('accounts/login', LoginView.as_view(), name='account_login'), 
        path('accounts/logout', LogoutView.as_view(), name='account_logout'), 
        # puedes sustituir por una pagina info
        path('accounts/signup',RedirectView.as_view(url='/store/product'), name='account_signup'),  
    ]
else:
    urlpatterns += [
        path('accounts/', include('allauth.urls')),
    ]