

from django.contrib import admin
from django.urls import path
from . import views as v

urlpatterns = [
    # CATEGORY
    path('category-list', v.category_list, name='category_list'),
    path('add-category', v.add_category, name='add_category'),
    path('edit-category/<str:id>', v.edit_category, name='edit_category'),

    # SUBCATEGORY
    path('subcategory-list', v.subcategory_list, name='subcategory_list'),
    path('add-subcategory', v.add_subcategory, name='add_subcategory'),
    path('edit-subcategory/<str:id>', v.edit_subcategory, name='edit_subcategory'),


    path('product-list', v.product_list, name='product_list'),
    path('add-product', v.add_product, name='add_product'),
    path('edit-product/<str:id>', v.edit_product, name='edit_product'),


]