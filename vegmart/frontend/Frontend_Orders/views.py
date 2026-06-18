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
def orders_list(request):
    token = request.session.get('token', False)
    if token:
        return render(request, 'Orders/orders-list.html')
    else:
        messages.error(request, 'Session expired. Please log in again.')
        return redirect('Frontend_User:login')


def place_order(request):
    token = request.session.get('token', False)

    if not token:
        messages.error(request, 'Session expired. Please log in again.')
        return redirect('Frontend_User:login')

    headers = {'Authorization': f'Bearer {token}'}

    try:
        # 🔹 Customers
        customers_url = hosturl + '/api/Customers/customerlist'
        customers_res = requests.get(customers_url, headers=headers)
        customers_data = customers_res.json().get('data', [])

        # 🔹 Product Variants (VERY IMPORTANT for order page)
        # variants_url = hosturl + '/api/Masters/productvariantlist'
        # variants_res = requests.get(variants_url, headers=headers)
        # variants_data = variants_res.json().get('data', [])
        # 🔹 Product Variants (VERY IMPORTANT for order page)
        categorys_url = hosturl + '/api/Masters/categorylist'
        categorys_res = requests.get(categorys_url, headers=headers)
        categorys_data = categorys_res.json().get('data', [])
        # 🔹 Product Variants (VERY IMPORTANT for order page)
        # brands_url = hosturl + '/api/Masters/productbrandlist'
        # brands_res = requests.get(brands_url, headers=headers)
        # brands_data = brands_res.json().get('data', [])
    except Exception as e:
        print("API ERROR:", e)
        customers_data = []
        # variants_data = []
        categorys_data=[]
        # brands_data=[]

    return render(
        request,
        'Orders/place-order.html',
        {
            "customers": customers_data,
            # "variants": variants_data,
            "categories":categorys_data,
            "brands":[]
        }
    )