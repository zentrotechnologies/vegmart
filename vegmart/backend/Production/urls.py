

from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('addprocessingbatch', addprocessingbatch.as_view()),
    path('addbatchoutput', addbatchoutput.as_view()),
    path('processingbatchlist', processingbatchlist.as_view()),
    path('batchdetails', batchdetails.as_view()),

]