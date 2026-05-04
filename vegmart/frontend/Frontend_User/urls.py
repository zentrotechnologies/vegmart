

from django.contrib import admin
from django.urls import path
from . import views as v

urlpatterns = [
    path('', v.login, name='login'),
    path('logout', v.logout, name='logout'),
    path('forgot_password', v.forgot_password, name='forgot_password'),

    path('dashboard/home', v.dashboard, name='dashboard'),
    path('customer-list', v.customer_list, name='customer_list'),
    path('vendor-list', v.vendor_list, name='vendor_list'),


    path('role-list', v.role_list, name='role_list'),


]