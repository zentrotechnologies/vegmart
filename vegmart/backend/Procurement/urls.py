

from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    # PROCUREMENT
    path('addprocuremententry', addprocuremententry.as_view()),
    path('procurementlist', procurementlist.as_view()),
    path('procurement_list_pagination_api', procurement_list_pagination_api.as_view()),
    path('procurementpayment', procurementpayment.as_view()),
    path('requirement_by_order', requirement_by_order.as_view()),


    path('addrawproductmaster', addrawproductmaster.as_view()),
    path('rawproductmasterlist', rawproductmasterlist.as_view()),
    path('rawproductmaster_list_pagination_api', rawproductmaster_list_pagination_api.as_view()),
    path('rawproductmasterupdate', rawproductmasterupdate.as_view()),
    path('rawproductmasterdelete', rawproductmasterdelete.as_view()),
    path('rawproductmasterbyid', rawproductmasterbyid.as_view()),


    path('createrecipe', createrecipe.as_view()),
    path('mappinglist', mappinglist.as_view()),
    path('mapping_list_pagination_api', mapping_list_pagination_api.as_view()),
    path('mappingupdate', mappingupdate.as_view()),
    path('mappingdelete', mappingdelete.as_view()),
    path('variant_grouped_mapping_list_pagination_api', variant_grouped_mapping_list_pagination_api.as_view()),
    path('get_mapping_by_product', get_mapping_by_product.as_view()),
    
    path('create_procurement', create_procurement.as_view()),
    path('procurement_details', procurement_details.as_view()),
    path('complete_procurement', complete_procurement.as_view()),
    path('delete_procurement', delete_procurement.as_view()),


    path('recipe_list_pagination_api', recipe_list_pagination_api.as_view()),
    path('activaterecipe',ActivateRecipeAPI.as_view()),
    path('deactivaterecipe',DeactivateRecipeAPI.as_view()),
    path('deleterecipe',DeleteRecipeAPI.as_view()),
    path('clonerecipe',CloneRecipeAPI.as_view()),
    path('recipe_details',recipe_details.as_view()),
    path('updaterecipe',UpdateRecipe.as_view()),
    path('get_product_recipe_list',get_product_recipe_list.as_view()),

]