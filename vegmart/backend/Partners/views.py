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
class addvendor(GenericAPIView):
    def post(self, request):
        data = {
            'name': str(request.data.get('name')).lower(),
            'phone': request.data.get('phone'),
            'address': request.data.get('address'),
        }

        if not data['name'] or not data['phone']:
            return Response({"data": {}, "response": {"n": 0, "msg": "Name & phone required", "status": "error"}})

        exist = Vendor.objects.filter(name=data['name'], phone=data['phone'], isActive=True).first()
        if exist:
            return Response({"data": {}, "response": {"n": 0, "msg": "Vendor already exists", "status": "error"}})

        serializer = VendorSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "response": {"n": 1, "msg": "Vendor added", "status": "success"}})

        first_key, first_value = next(iter(serializer.errors.items()))
        return Response({"data": serializer.errors, "response": {"n": 0, "msg": first_key+' : '+first_value[0], "status": "error"}})
    

class vendorlist(GenericAPIView):
    def get(self, request):
        objs = Vendor.objects.filter(isActive=True).order_by('id')
        serializer = VendorSerializer(objs, many=True)

        return Response({
            "data": serializer.data,
            "response": {"n": 1, "msg": "Vendor list", "status": "success"}
        })
class vendor_list_pagination_api(GenericAPIView):
    pagination_class = CustomPagination

    def post(self, request):
        objs = Vendor.objects.filter(isActive=True).order_by('-id')

        search = request.data.get('search')
        if search:
            objs = objs.filter(
                Q(name__icontains=search) |
                Q(phone__icontains=search) |
                Q(address__icontains=search)
            )

        page = self.paginate_queryset(objs)
        serializer = VendorSerializer(page, many=True)

        return self.get_paginated_response(serializer.data)

class vendorupdate(GenericAPIView):
    def post(self, request):
        id = request.data.get('vendorid')
        obj = Vendor.objects.filter(id=id, isActive=True).first()

        if not obj:
            return Response({"data": '', "response": {"n": 0, "msg": "Vendor not found", "status": "error"}})

        data = {
            'name': str(request.data.get('name')).lower(),
            'phone': request.data.get('phone'),
            'address': request.data.get('address'),
        }

        serializer = VendorSerializer(obj, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "response": {"n": 1, "msg": "Vendor updated", "status": "success"}})

        first_key, first_value = next(iter(serializer.errors.items()))
        return Response({"data": serializer.errors, "response": {"n": 0, "msg": first_key+' : '+first_value[0], "status": "error"}})

class vendorbyid(GenericAPIView):
    def post(self, request):
        id = request.data.get('vendorid')
        obj = Vendor.objects.filter(id=id, isActive=True).first()

        if obj:
            serializer = VendorSerializer(obj)
            return Response({"data": serializer.data, "response": {"n": 1, "msg": "Vendor found", "status": "success"}})

        return Response({"data": '', "response": {"n": 0, "msg": "Vendor not found", "status": "error"}})

class vendordelete(GenericAPIView):
    def post(self, request):
        id = request.data.get('vendorid')
        obj = Vendor.objects.filter(id=id, isActive=True).first()

        if not obj:
            return Response({"data": '', "response": {"n": 0, "msg": "Vendor not found", "status": "error"}})

        serializer = VendorSerializer(obj, data={'isActive': False}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "response": {"n": 1, "msg": "Vendor deleted", "status": "success"}})

        first_key, first_value = next(iter(serializer.errors.items()))
        return Response({"data": serializer.errors, "response": {"n": 0, "msg": first_key+' : '+first_value[0], "status": "error"}})

class adddeliveryagent(GenericAPIView):
    def post(self, request):
        data = {
            'name': str(request.data.get('name')).lower(),
            'phone': request.data.get('phone'),
        }

        if not data['name'] or not data['phone']:
            return Response({"data": {}, "response": {"n": 0, "msg": "Name & phone required", "status": "error"}})

        exist = DeliveryAgent.objects.filter(name=data['name'], phone=data['phone'], isActive=True).first()
        if exist:
            return Response({"data": {}, "response": {"n": 0, "msg": "Agent already exists", "status": "error"}})

        serializer = DeliveryAgentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "response": {"n": 1, "msg": "Delivery agent added", "status": "success"}})

        first_key, first_value = next(iter(serializer.errors.items()))
        return Response({"data": serializer.errors, "response": {"n": 0, "msg": first_key+' : '+first_value[0], "status": "error"}})

class deliveryagentlist(GenericAPIView):
    def get(self, request):
        objs = DeliveryAgent.objects.filter(isActive=True).order_by('id')
        serializer = DeliveryAgentSerializer(objs, many=True)

        return Response({
            "data": serializer.data,
            "response": {"n": 1, "msg": "Agent list", "status": "success"}
        })

class deliveryagent_list_pagination_api(GenericAPIView):
    pagination_class = CustomPagination

    def post(self, request):
        objs = DeliveryAgent.objects.filter(isActive=True).order_by('-id')

        search = request.data.get('search')
        if search:
            objs = objs.filter(
                Q(name__icontains=search) |
                Q(phone__icontains=search)
            )

        page = self.paginate_queryset(objs)
        serializer = DeliveryAgentSerializer(page, many=True)

        return self.get_paginated_response(serializer.data)

class deliveryagentupdate(GenericAPIView):
    def post(self, request):
        id = request.data.get('agentid')
        obj = DeliveryAgent.objects.filter(id=id, isActive=True).first()

        if not obj:
            return Response({"data": '', "response": {"n": 0, "msg": "Agent not found", "status": "error"}})

        data = {
            'name': str(request.data.get('name')).lower(),
            'phone': request.data.get('phone'),
        }

        serializer = DeliveryAgentSerializer(obj, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "response": {"n": 1, "msg": "Agent updated", "status": "success"}})

        first_key, first_value = next(iter(serializer.errors.items()))
        return Response({"data": serializer.errors, "response": {"n": 0, "msg": first_key+' : '+first_value[0], "status": "error"}})

class deliveryagentbyid(GenericAPIView):
    def post(self, request):
        id = request.data.get('agentid')
        obj = DeliveryAgent.objects.filter(id=id, isActive=True).first()

        if obj:
            serializer = DeliveryAgentSerializer(obj)
            return Response({"data": serializer.data, "response": {"n": 1, "msg": "Agent found", "status": "success"}})

        return Response({"data": '', "response": {"n": 0, "msg": "Agent not found", "status": "error"}})


class deliveryagentdelete(GenericAPIView):
    def post(self, request):
        id = request.data.get('agentid')
        obj = DeliveryAgent.objects.filter(id=id, isActive=True).first()

        if not obj:
            return Response({"data": '', "response": {"n": 0, "msg": "Agent not found", "status": "error"}})

        serializer = DeliveryAgentSerializer(obj, data={'isActive': False}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "response": {"n": 1, "msg": "Agent deleted", "status": "success"}})

        first_key, first_value = next(iter(serializer.errors.items()))
        return Response({"data": serializer.errors, "response": {"n": 0, "msg": first_key+' : '+first_value[0], "status": "error"}})



















