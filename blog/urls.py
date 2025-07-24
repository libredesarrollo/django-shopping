from django.urls import path

from .views import PostIndex, PostShow, PostSitemap

urlpatterns = [
    path('', PostIndex.as_view(), name='b.index'),
    path('sitemap.xml', PostSitemap.as_view(), name='b.sitemap'),
    # path('<int:pk>', PostShow.as_view() )
    path('<slug:slug>', PostShow.as_view(), name='b.show')
]