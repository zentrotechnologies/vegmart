from django.shortcuts import render

# Create your views here.from rest_framework.response import Response
from rest_framework.authentication import (BaseAuthentication,
                                           get_authorization_header)
from rest_framework import permissions
from rest_framework.response import Response
import json
from rest_framework.generics import GenericAPIView
from django.contrib.auth import authenticate
from .models import *
from .serializers import *
from User.jwt import userJWTAuthentication
from django.template.loader import get_template, render_to_string
from django.core.mail import EmailMessage
from User.common import CustomPagination
from django.db.models import Q
# Create your views here.
class addcustomer(GenericAPIView):
    def post(self, request):
        data = {
            'name': str(request.data.get('name')).lower(),
            'mobile': request.data.get('mobile'),
            'address_line1': request.data.get('address_line1'),
            'address_line2': request.data.get('address_line2'),
            'area': request.data.get('area'),
            'city': request.data.get('city'),
            'pincode': request.data.get('pincode'),
            'gst_number': request.data.get('gst_number'),
            'customer_type': request.data.get('customer_type'),
            'default_credit_days': request.data.get('default_credit_days') or 0,
            'outstanding_balance': request.data.get('outstanding_balance') or 0,
        }

        if not data['name'] or not data['mobile']:
            return Response({"data": {}, "response": {"n": 0, "msg": "Name & mobile required", "status": "error"}})

        exist = Customer.objects.filter(mobile=data['mobile'], isActive=True).first()
        if exist:
            return Response({"data": {}, "response": {"n": 0, "msg": "Customer already exists", "status": "error"}})

        serializer = CustomerSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "response": {"n": 1, "msg": "Customer added", "status": "success"}})

        first_key, first_value = next(iter(serializer.errors.items()))
        return Response({"data": serializer.errors, "response": {"n": 0, "msg": first_key+' : '+first_value[0], "status": "error"}})
    
class customerlist(GenericAPIView):
    def get(self, request):
        objs = Customer.objects.filter(isActive=True).order_by('id')
        serializer = CustomerSerializer(objs, many=True)

        return Response({
            "data": serializer.data,
            "response": {"n": 1, "msg": "Customer list", "status": "success"}
        })
class customer_list_pagination_api(GenericAPIView):
    pagination_class = CustomPagination

    def post(self, request):
        objs = Customer.objects.filter(isActive=True).order_by('-id')

        search = request.data.get('search')
        if search:
            objs = objs.filter(
                Q(name__icontains=search) |
                Q(mobile__icontains=search) |
                Q(city__icontains=search) |
                Q(area__icontains=search) |
                Q(gst_number__icontains=search)
            )

        page = self.paginate_queryset(objs)
        serializer = CustomerSerializer(page, many=True)

        return self.get_paginated_response(serializer.data)

class customerupdate(GenericAPIView):
    def post(self, request):
        id = request.data.get('customerid')
        obj = Customer.objects.filter(id=id, isActive=True).first()

        if not obj:
            return Response({"data": '', "response": {"n": 0, "msg": "Customer not found", "status": "error"}})

        data = {
            'name': str(request.data.get('name')).lower(),
            'mobile': request.data.get('mobile'),
            'address_line1': request.data.get('address_line1'),
            'address_line2': request.data.get('address_line2'),
            'area': request.data.get('area'),
            'city': request.data.get('city'),
            'pincode': request.data.get('pincode'),
            'gst_number': request.data.get('gst_number'),
            'customer_type': request.data.get('customer_type'),
            'default_credit_days': request.data.get('default_credit_days'),
            'outstanding_balance': request.data.get('outstanding_balance'),
        }

        # prevent duplicate mobile
        if Customer.objects.filter(mobile=data['mobile'], isActive=True).exclude(id=id).exists():
            return Response({"data": '', "response": {"n": 0, "msg": "Mobile already exists", "status": "error"}})

        serializer = CustomerSerializer(obj, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "response": {"n": 1, "msg": "Customer updated", "status": "success"}})

        first_key, first_value = next(iter(serializer.errors.items()))
        return Response({"data": serializer.errors, "response": {"n": 0, "msg": first_key+' : '+first_value[0], "status": "error"}})


class customerbyid(GenericAPIView):
    def post(self, request):
        id = request.data.get('customerid')
        obj = Customer.objects.filter(id=id, isActive=True).first()

        if obj:
            serializer = CustomerSerializer(obj)
            return Response({"data": serializer.data, "response": {"n": 1, "msg": "Customer found", "status": "success"}})

        return Response({"data": '', "response": {"n": 0, "msg": "Customer not found", "status": "error"}})

class customerdelete(GenericAPIView):
    def post(self, request):
        id = request.data.get('customerid')
        obj = Customer.objects.filter(id=id, isActive=True).first()

        if not obj:
            return Response({"data": '', "response": {"n": 0, "msg": "Customer not found", "status": "error"}})

        serializer = CustomerSerializer(obj, data={'isActive': False}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "response": {"n": 1, "msg": "Customer deleted", "status": "success"}})

        first_key, first_value = next(iter(serializer.errors.items()))
        return Response({"data": serializer.errors, "response": {"n": 0, "msg": first_key+' : '+first_value[0], "status": "error"}})




















































