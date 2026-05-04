from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    # VEHICLE
    path('addvehicle', addvehicle.as_view()),
    path('vehiclelist', vehiclelist.as_view()),
    path('vehicle_list_pagination_api', vehicle_list_pagination_api.as_view()),
    path('vehicleupdate', vehicleupdate.as_view()),
    path('vehicledelete', vehicledelete.as_view()),
    path('vehiclebyid', vehiclebyid.as_view()),

    # LOGISTICS ORDER
    path('addlogisticsorder', addlogisticsorder.as_view()),
    path('logisticsorderlist', logisticsorderlist.as_view()),
    path('logisticsorder_list_pagination_api', logisticsorder_list_pagination_api.as_view()),
    path('logisticsorderupdate', logisticsorderupdate.as_view()),
    path('logisticsorderdelete', logisticsorderdelete.as_view()),
    path('logisticsorderbyid', logisticsorderbyid.as_view()),

    # DELIVERY
    path('adddelivery', adddelivery.as_view()),
    path('deliverylist', deliverylist.as_view()),
    path('delivery_list_pagination_api', delivery_list_pagination_api.as_view()),
    path('deliveryupdate', deliveryupdate.as_view()),
    path('deliverydelete', deliverydelete.as_view()),
    path('deliverybyid', deliverybyid.as_view()),
]