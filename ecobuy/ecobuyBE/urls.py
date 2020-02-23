from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('/test', views.index, name='s'),
    path('user_buy_product', views.user_buy_product, name='user_buy_product')
]

urlpatterns = format_suffix_patterns(urlpatterns)