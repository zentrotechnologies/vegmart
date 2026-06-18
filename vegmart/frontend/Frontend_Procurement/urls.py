

from django.contrib import admin
from django.urls import path
from . import views as v

urlpatterns = [
    path('procurement-list', v.procurement_list, name='procurement-list'),
    path('procurement-item-list', v.procurement_item_list, name='procurement-item-list'),
    path('procurement-item-mapping-list', v.procurement_item_mapping_list, name='procurement-item-mapping-list'),
    path('create-recipe', v.create_recipe, name='create-recipe'),
    path('view-recipe/<int:id>',v.view_recipe, name='view-recipe'),
    path('edit-recipe/<int:id>',v.edit_recipe,name='edit-recipe'),
]