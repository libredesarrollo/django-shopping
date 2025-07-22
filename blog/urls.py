from django.urls import path

from .views import PostIndex, PostShow

urlpatterns = [
    path('', PostIndex.as_view(), name='b.index'),
    # path('<int:pk>', PostShow.as_view() )
    path('<slug:slug>', PostShow.as_view(), name='b.show')
]