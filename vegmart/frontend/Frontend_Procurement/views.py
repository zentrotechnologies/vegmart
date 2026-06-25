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
        headers = {'Authorization': f'Bearer {token}'}

        units_url = hosturl + '/api/Masters/unitlist'
        units_res = requests.get(units_url, headers=headers)
        units = units_res.json().get('data', [])
        return render(request, 'Procurement/procurement-item-list.html',{'units':units})
    else:
        messages.error(request, 'Session expired. Please log in again.')
        return redirect('Frontend_User:login')
    
#recipe amaster list
def procurement_item_mapping_list(request):
    token = request.session.get('token', False)
    if token:
        return render(request, 'Recipe/recipe-list.html')
    else:
        messages.error(request, 'Session expired. Please log in again.')
        return redirect('Frontend_User:login')
    

def create_recipe(request):
    token = request.session.get('token', False)
    if token:


        headers = {'Authorization': f'Bearer {token}'}
        products_url = hosturl + '/api/Masters/productlist'
        products_res = requests.get(products_url, headers=headers)
        products_data = products_res.json().get('data', [])
        
        
        raw_materials_url = hosturl + '/api/Procurement/rawproductmasterlist'
        raw_materials_res = requests.post(raw_materials_url, headers=headers)
        raw_materials = raw_materials_res.json().get('data', [])
        
        
        units_url = hosturl + '/api/Masters/unitlist'
        units_res = requests.get(units_url, headers=headers)
        units = units_res.json().get('data', [])
        return render(request, 'Recipe/create-recipe.html',{"products":products_data,"raw_materials":raw_materials,"units":units})
    else:
        messages.error(request, 'Session expired. Please log in again.')
        return redirect('Frontend_User:login')

def view_recipe(request, id):

    token = request.session.get('token', False)

    if token:
        headers = {'Authorization': f'Bearer {token}'}

        recipe_url = hosturl + f'/api/Procurement/recipe_details?recipe_id={id}'
        recipe_res = requests.get(recipe_url, headers=headers)
        recipe = recipe_res.json().get('data',{})
        
        return render(
            request,
            'Recipe/view-recipe.html',
            {
                "recipe": recipe,
                "raw_materials": recipe.get(
                    'raw_materials',
                    []
                )
            }
        )

    messages.error(
        request,
        'Session expired. Please log in again.'
    )

    return redirect('Frontend_User:login')

def edit_recipe(request, id):

    token = request.session.get('token', False)

    if not token:
        messages.error(
            request,
            'Session expired. Please log in again.'
        )
        return redirect('Frontend_User:login')

    try:

        headers = {
            'Authorization': f'Bearer {token}'
        }

        # Recipe Details
        recipe_url = (
            hosturl +
            f'/api/Procurement/recipe_details?recipe_id={id}'
        )

        recipe_res = requests.get(
            recipe_url,
            headers=headers
        )

        recipe = recipe_res.json().get(
            'data',
            {}
        )

        # Products
        products_url = (
            hosturl +
            '/api/Masters/productlist'
        )

        products_res = requests.get(
            products_url,
            headers=headers
        )

        products = products_res.json().get(
            'data',
            []
        )

        # Raw Materials
        raw_materials_url = (
            hosturl +
            '/api/Procurement/rawproductmasterlist'
        )

        raw_materials_res = requests.post(
            raw_materials_url,
            headers=headers
        )

        raw_materials = raw_materials_res.json().get(
            'data',
            []
        )

        # Units
        units_url = (
            hosturl +
            '/api/Masters/unitlist'
        )

        units_res = requests.get(
            units_url,
            headers=headers
        )

        units = units_res.json().get(
            'data',
            []
        )

        return render(
            request,
            'Recipe/edit-recipe.html',
            {
                "recipe": recipe,
                "products": products,
                "raw_materials": raw_materials,
                "units": units
            }
        )

    except Exception as e:

        messages.error(
            request,
            str(e)
        )

        return redirect(
            'Frontend_Procurement:procurement-item-mapping-list'
        )
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        