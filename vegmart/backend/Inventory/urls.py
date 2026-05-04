from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    # WAREHOUSE
    path('addwarehouse', addwarehouse.as_view()),
    path('warehouselist', warehouselist.as_view()),
    path('warehouse_list_pagination_api', warehouse_list_pagination_api.as_view()),
    path('warehouseupdate', warehouseupdate.as_view()),
    path('warehousedelete', warehousedelete.as_view()),
    path('warehousebyid', warehousebyid.as_view()),

    # BATCH
    path('addbatch', addbatch.as_view()),
    path('batchlist', batchlist.as_view()),
    path('batch_list_pagination_api', batch_list_pagination_api.as_view()),
    path('batchupdate', batchupdate.as_view()),
    path('batchdelete', batchdelete.as_view()),
    path('batchbyid', batchbyid.as_view()),
    
    path('inventorylist', inventorylist.as_view()),
    path('inventory_list_pagination_api', inventory_list_pagination_api.as_view()),
    path('inventoryupdate', inventoryupdate.as_view()),
    path('inventorydelete', inventorydelete.as_view()),

]