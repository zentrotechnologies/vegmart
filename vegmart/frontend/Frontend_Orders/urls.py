

from django.contrib import admin
from django.urls import path
from . import views as v

urlpatterns = [
    path('orders-list', v.orders_list, name='orders-list'),

    path('place-order', v.place_order, name='place-order'),

]