
from django.contrib import admin
from django.urls import path
from . import views as v

urlpatterns = [
    path('production-list', v.production_list, name='production-list'),
]