
from django.contrib import admin
from django.urls import path
from . import views as v

urlpatterns = [
    path('production-list', v.production_list, name='production-list'),
    path('create', v.create, name='create'),
    path('details/<str:id>', v.details, name='details'),
    path('complete/<str:id>', v.complete, name='complete'),
    path('order-production/<str:id>', v.order_production, name='order-production'),
    
]