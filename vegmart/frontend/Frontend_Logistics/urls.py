

from django.contrib import admin
from django.urls import path
from . import views as v

urlpatterns = [
    path('delivery-list', v.delivery_list, name='delivery-list'),


]