from django.shortcuts import render, redirect, HttpResponse,HttpResponseRedirect
import requests
import os
import json
from datetime import datetime,date,timedelta
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
import datetime
from datetime import date
from helpers.validations import hosturl



# Create your views here.
def procurement_list(request):
    token = request.session.get('token', False)
    if token:
        return render(request, 'Procurement/procurement-list.html')
    else:
        messages.error(request, 'Session expired. Please log in again.')
        return redirect('Frontend_User:login')
    

def procurement_item_list(request):
    token = request.session.get('token', False)
    if token:
        return render(request, 'Procurement/procurement-item-list.html')
    else:
        messages.error(request, 'Session expired. Please log in again.')
        return redirect('Frontend_User:login')
    

def procurement_item_mapping_list(request):
    token = request.session.get('token', False)
    if token:
        return render(request, 'Procurement/procurement-item-mapping-list.html')
    else:
        messages.error(request, 'Session expired. Please log in again.')
        return redirect('Frontend_User:login')
    















