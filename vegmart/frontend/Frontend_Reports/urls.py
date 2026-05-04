

from django.contrib import admin
from django.urls import path
from . import views as v

urlpatterns = [
    path('reports-list', v.reports_list, name='reports-list'),


]