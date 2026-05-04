from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    # CATEGORY
    path('addcategory', addcategory.as_view()),
    path('categorylist', categorylist.as_view()),
    path('category_list_pagination_api', category_list_pagination_api.as_view()),
    path('categoryupdate', categoryupdate.as_view()),
    path('categorydelete', categorydelete.as_view()),
    path('categorybyid', categorybyid.as_view()),

    # SUBCATEGORY
    path('addsubcategory', addsubcategory.as_view()),
    path('subcategorylist', subcategorylist.as_view()),
    path('subcategory_list_pagination_api', subcategory_list_pagination_api.as_view()),
    path('subcategoryupdate', subcategoryupdate.as_view()),
    path('subcategorydelete', subcategorydelete.as_view()),
    path('subcategorybyid', subcategorybyid.as_view()),



    # PRODUCT
    path('addproduct', addproduct.as_view()),
    path('productlist', productlist.as_view()),
    path('procurementreadyproductlist', procurementreadyproductlist.as_view()),

    path('product_list_pagination_api', product_list_pagination_api.as_view()),
    path('productupdate', productupdate.as_view()),
    path('productdelete', productdelete.as_view()),
    path('productbyid', productbyid.as_view()),

    # PRODUCT VARIANT
    path('addproductvariant', addproductvariant.as_view()),
    path('productvariantlist', productvariantlist.as_view()),
    path('getprocurementexpectedproductvariantlist', getprocurementexpectedproductvariantlist.as_view()),

    path('productvariant_list_pagination_api', productvariant_list_pagination_api.as_view()),
    path('productvariantupdate', productvariantupdate.as_view()),
    path('productvariantdelete', productvariantdelete.as_view()),
    path('productvariantbyid', productvariantbyid.as_view()),

    path('productvariantbyproduct', productvariantbyproduct.as_view()),





]