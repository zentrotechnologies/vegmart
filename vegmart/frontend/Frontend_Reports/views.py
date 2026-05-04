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



def reports_list(request):
    token = request.session.get('token', False)
    if token:
        return render(request, 'wip.html')
    else:
        messages.error(request, 'Session expired. Please log in again.')
        return redirect('Frontend_User:login')
