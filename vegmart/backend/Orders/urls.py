from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
        path('createorder', createorder.as_view()),
        path('customerorderlist', customerorderlist.as_view()),
        path('orderdetails', orderdetails.as_view()),

        # admin
        path('confirmorder', confirmorder.as_view()),
        path('dispatchorder', dispatchorder.as_view()),
        path('cancelorder', cancelorder.as_view()),
        path('deliverorder', deliverorder.as_view()),
        path('order_list_pagination_api', order_list_pagination_api.as_view()),

        # payment
        path('addpayment', addpayment.as_view()),
        path('deleteorder', deleteorder.as_view()),




]