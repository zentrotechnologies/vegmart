from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('addcustomer', addcustomer.as_view()),
    path('customerlist', customerlist.as_view()),
    path('customer_list_pagination_api', customer_list_pagination_api.as_view()),
    path('customerupdate', customerupdate.as_view()),
    path('customerdelete', customerdelete.as_view()),
    path('customerbyid', customerbyid.as_view()),

]