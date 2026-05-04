

from django.contrib import admin
from django.urls import path
from . import views as v

urlpatterns = [
    path('inventory-list', v.inventory_list, name='inventory-list'),


]