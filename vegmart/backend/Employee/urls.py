from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    # CATEGORY
    path('addemployee', addemployee.as_view()),
    path('employeelist', employeelist.as_view()),
    path('employee_list_pagination_api', employee_list_pagination_api.as_view()),
    path('employeeupdate', employeeupdate.as_view()),
    path('employeedelete', employeedelete.as_view()),
    path('employeebyid', employeebyid.as_view()),




]