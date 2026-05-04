

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


    path('addprocurementitemmaster', addprocurementitemmaster.as_view()),
    path('procurementitemmasterlist', procurementitemmasterlist.as_view()),
    path('procurementitemmaster_list_pagination_api', procurementitemmaster_list_pagination_api.as_view()),
    path('procurementitemmasterupdate', procurementitemmasterupdate.as_view()),
    path('procurementitemmasterdelete', procurementitemmasterdelete.as_view()),
    path('procurementitemmasterbyid', procurementitemmasterbyid.as_view()),


    path('addmapping', addmapping.as_view()),
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

]