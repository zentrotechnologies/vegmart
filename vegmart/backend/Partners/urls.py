

from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [

    # VENDOR
    path('addvendor', addvendor.as_view()),
    path('vendorlist', vendorlist.as_view()),
    path('vendor_list_pagination_api', vendor_list_pagination_api.as_view()),
    path('vendorupdate', vendorupdate.as_view()),
    path('vendordelete', vendordelete.as_view()),
    path('vendorbyid', vendorbyid.as_view()),

    # DELIVERY AGENT
    path('adddeliveryagent', adddeliveryagent.as_view()),
    path('deliveryagentlist', deliveryagentlist.as_view()),
    path('deliveryagent_list_pagination_api', deliveryagent_list_pagination_api.as_view()),
    path('deliveryagentupdate', deliveryagentupdate.as_view()),
    path('deliveryagentdelete', deliveryagentdelete.as_view()),
    path('deliveryagentbyid', deliveryagentbyid.as_view()),

]