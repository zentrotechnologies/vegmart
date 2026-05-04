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
# CATEGORY APIs
add_category_url = hosturl + "/api/Masters/addcategory"
edit_category_url = hosturl + "/api/Masters/categoryupdate"
get_category_url = hosturl + "/api/Masters/categorybyid"
get_category_list_url = hosturl + "/api/Masters/categorylist"


# SUBCATEGORY APIs
add_subcategory_url = hosturl + "/api/Masters/addsubcategory"
edit_subcategory_url = hosturl + "/api/Masters/subcategoryupdate"
get_subcategory_url = hosturl + "/api/Masters/subcategorybyid"
get_subcategory_list_url = hosturl + "/api/Masters/subcategorylist"


# CATEGORY APIs
add_product_url = hosturl + "/api/Masters/addproduct"
edit_product_url = hosturl + "/api/Masters/productupdate"
get_product_url = hosturl + "/api/Masters/productbyid"
get_product_list_url = hosturl + "/api/Masters/productlist"


def category_list(request):
    token = request.session.get('token', False)
    if token:
        return render(request, 'Masters/Category/category_list.html')
    else:
        messages.error(request, 'Session expired. Please log in again.')
        return redirect('Frontend_User:login')

def add_category(request):
    token = request.session.get('token', False)
    if token:
        headers = {'Authorization': f'Bearer {token}'}

        if request.method == 'POST':
            data = request.POST.copy()

            response = requests.post(add_category_url, data=data, headers=headers)
            return HttpResponse(json.dumps(response.json()), content_type='application/json')

        else:
            return render(request, 'Masters/Category/add_category.html')

    else:
        messages.error(request, 'Session expired. Please log in again.')
        return redirect('Frontend_User:login')


def edit_category(request, id):
    token = request.session.get('token', False)

    if token:
        headers = {'Authorization': f'Bearer {token}'}

        if request.method == 'POST':
            data = request.POST.copy()

            response = requests.post(edit_category_url, data=data, headers=headers)
            return HttpResponse(json.dumps(response.json()), content_type='application/json')

        else:
            data = {'categoryid': id}
            response = requests.post(get_category_url, data=data, headers=headers)

            return render(
                request,
                'Masters/Category/edit_category.html',
                {'category': response.json()['data']}
            )

    else:
        messages.error(request, 'Session expired. Please log in again.')
        return redirect('Frontend_User:login')


def subcategory_list(request):
    token = request.session.get('token', False)
    if token:
        return render(request, 'Masters/SubCategory/subcategory_list.html')
    else:
        messages.error(request, 'Session expired. Please log in again.')
        return redirect('Frontend_User:login')

def add_subcategory(request):
    token = request.session.get('token', False)

    if token:
        headers = {'Authorization': f'Bearer {token}'}

        if request.method == 'POST':
            data = request.POST.copy()

            response = requests.post(add_subcategory_url, data=data, headers=headers)
            return HttpResponse(json.dumps(response.json()), content_type='application/json')

        else:
            # 🔥 get categories for dropdown
            cat_response = requests.get(get_category_list_url, headers=headers)

            return render(
                request,
                'Masters/SubCategory/add_subcategory.html',
                {'categories': cat_response.json()['data']}
            )

    else:
        messages.error(request, 'Session expired. Please log in again.')
        return redirect('Frontend_User:login')

def edit_subcategory(request, id):
    token = request.session.get('token', False)

    if token:
        headers = {'Authorization': f'Bearer {token}'}

        if request.method == 'POST':
            data = request.POST.copy()

            response = requests.post(edit_subcategory_url, data=data, headers=headers)
            return HttpResponse(json.dumps(response.json()), content_type='application/json')

        else:
            data = {'subcategoryid': id}

            sub_response = requests.post(get_subcategory_url, data=data, headers=headers)
            cat_response = requests.get(get_category_list_url, headers=headers)

            return render(
                request,
                'Masters/SubCategory/edit_subcategory.html',
                {
                    'subcategory': sub_response.json()['data'],
                    'categories': cat_response.json()['data']
                }
            )

    else:
        messages.error(request, 'Session expired. Please log in again.')
        return redirect('Frontend_User:login')





def product_list(request):
    token = request.session.get('token', False)
    if token:
        return render(request, 'Masters/Product/product_list.html')
    else:
        messages.error(request, 'Session expired. Please log in again.')
        return redirect('Frontend_User:login')

def add_product(request):
    token = request.session.get('token', False)
    if token:
        headers = {'Authorization': f'Bearer {token}'}

        if request.method == 'POST':
            data = request.POST.copy()

            response = requests.post(add_product_url, data=data, headers=headers,files=request.FILES)
            return HttpResponse(json.dumps(response.json()), content_type='application/json')

        else:

            # 🔥 get categories for dropdown
            cat_response = requests.get(get_category_list_url, headers=headers)


            return render(request, 'Masters/Product/add_product.html',{'categories': cat_response.json()['data']})

    else:
        messages.error(request, 'Session expired. Please log in again.')
        return redirect('Frontend_User:login')

def edit_product(request, id):
    token = request.session.get('token', False)

    if not token:
        messages.error(request, 'Session expired. Please log in again.')
        return redirect('Frontend_User:login')

    headers = {'Authorization': f'Bearer {token}'}

    # 🔹 POST → UPDATE
    if request.method == 'POST':
        data = request.POST.copy()

        response = requests.post(edit_product_url, data=data, headers=headers,files=request.FILES)

        try:
            return HttpResponse(json.dumps(response.json()), content_type='application/json')
        except:
            return HttpResponse(json.dumps({
                "response": {"n": 0, "msg": "Server error", "status": "error"}
            }), content_type='application/json')

    # 🔹 GET → LOAD DATA
    else:
        try:
            # Product details
            product_res = requests.post(get_product_url, data={'productid': id}, headers=headers)
            product_data = product_res.json().get('data', {})

            # Categories
            cat_res = requests.get(get_category_list_url, headers=headers)
            categories = cat_res.json().get('data', [])

            # Subcategories
            scat_res = requests.get(get_subcategory_list_url, headers=headers)
            subcategories = scat_res.json().get('data', [])

            # 🔥 IMPORTANT: GET VARIANTS
            variant_res = requests.post(
                hosturl + "/api/Masters/productvariantbyproduct",
                data={'productid': id},
                headers=headers
            )
            variants = variant_res.json().get('data', [])
            print("variants",variants)
        except Exception as e:
            print("Error:", e)
            messages.error(request, 'Something went wrong')
            return redirect('/masters/product-list')

        return render(
            request,
            'Masters/Product/edit_product.html',
            {
                'product': product_data,
                'categories': categories,
                'subcategories': subcategories,
                'variants': variants   # 🔥 REQUIRED FOR FRONTEND
            }
        )





