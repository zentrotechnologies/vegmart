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
def production_list(request):
    token = request.session.get('token', False)
    if token:
        return render(request, 'Production/production-list.html')
    else:
        messages.error(request, 'Session expired. Please log in again.')
        return redirect('Frontend_User:login')
    
    
def create(request):
    token = request.session.get('token', False)
    if token:
        return render(request, 'Production/create-production.html')
    else:
        messages.error(request, 'Session expired. Please log in again.')
        return redirect('Frontend_User:login')
    
    
def details(request,id):
    token = request.session.get('token', False)
    if token:
        context = {
            "production_id": id
        }

        return render(
            request,
            "Production/production-details.html",
            context
        )
    else:
        messages.error(request, 'Session expired. Please log in again.')
        return redirect('Frontend_User:login')
    
def complete(request,id):
    token = request.session.get('token', False)
    if token:
        context = {
            "production_id": id
        }

        return render(
            request,
            "Production/complete-production.html",
            context
        )
    else:
        messages.error(request, 'Session expired. Please log in again.')
        return redirect('Frontend_User:login')
    
def order_production(request,id):
    token = request.session.get('token', False)
    if token:
        context = {
            "order_id": id
        }

        return render(
            request,
            "Production/order-production.html",
            context
        )
    else:
        messages.error(request, 'Session expired. Please log in again.')
        return redirect('Frontend_User:login')
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    