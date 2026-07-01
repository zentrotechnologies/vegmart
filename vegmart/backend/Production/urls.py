

from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('addprocessingbatch', addprocessingbatch.as_view()),
    path('addbatchoutput', addbatchoutput.as_view()),
    path('processingbatchlist', processingbatchlist.as_view()),
    path('batchdetails', batchdetails.as_view()),
    
    path('production_list_pagination_api', production_list_pagination_api.as_view()),
    path('generate_recommendation', generate_recommendation.as_view()),
    path('create_production', create_production.as_view()),
    path('production_details', production_details.as_view()),
    path('complete_production', complete_production.as_view()),
    path('production_dashboard_api', production_dashboard_api.as_view()),
    path('delete_production', delete_production.as_view()),
    path('order_production_recommendation', order_production_recommendation.as_view()),
    path('create_order_production', create_order_production.as_view()),

]