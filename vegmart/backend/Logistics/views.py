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
class addvehicle(GenericAPIView):
    def post(self, request):
        data = {
            'number': str(request.data.get('number')).upper(),
            'capacity': request.data.get('capacity')
        }

        if not data['number']:
            return Response({"data": {}, "response": {"n": 0, "msg": "Vehicle number required", "status": "error"}})

        if Vehicle.objects.filter(number=data['number'], isActive=True).exists():
            return Response({"data": {}, "response": {"n": 0, "msg": "Vehicle already exists", "status": "error"}})

        serializer = VehicleSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "response": {"n": 1, "msg": "Vehicle added", "status": "success"}})

        first_key, first_value = next(iter(serializer.errors.items()))
        return Response({"data": serializer.errors, "response": {"n": 0, "msg": first_key+' : '+first_value[0], "status": "error"}})
    
class vehiclelist(GenericAPIView):
    def get(self, request):
        objs = Vehicle.objects.filter(isActive=True).order_by('id')
        serializer = VehicleSerializer(objs, many=True)

        return Response({
            "data": serializer.data,
            "response": {"n": 1, "msg": "Vehicle list", "status": "success"}
        })

class vehicle_list_pagination_api(GenericAPIView):
    pagination_class = CustomPagination

    def post(self, request):
        objs = Vehicle.objects.filter(isActive=True).order_by('-id')

        search = request.data.get('search')
        if search:
            objs = objs.filter(number__icontains=search)

        page = self.paginate_queryset(objs)
        serializer = VehicleSerializer(page, many=True)

        return self.get_paginated_response(serializer.data)

class vehicleupdate(GenericAPIView):
    def post(self, request):
        id = request.data.get('vehicleid')
        obj = Vehicle.objects.filter(id=id, isActive=True).first()

        if not obj:
            return Response({"data": '', "response": {"n": 0, "msg": "Vehicle not found", "status": "error"}})

        data = {
            'number': str(request.data.get('number')).upper(),
            'capacity': request.data.get('capacity')
        }

        serializer = VehicleSerializer(obj, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "response": {"n": 1, "msg": "Vehicle updated", "status": "success"}})

        first_key, first_value = next(iter(serializer.errors.items()))
        return Response({"data": serializer.errors, "response": {"n": 0, "msg": first_key+' : '+first_value[0], "status": "error"}})
class vehiclebyid(GenericAPIView):
    def post(self, request):
        id = request.data.get('vehicleid')
        obj = Vehicle.objects.filter(id=id, isActive=True).first()

        if obj:
            serializer = VehicleSerializer(obj)
            return Response({"data": serializer.data, "response": {"n": 1, "msg": "Vehicle found", "status": "success"}})

        return Response({"data": '', "response": {"n": 0, "msg": "Vehicle not found", "status": "error"}})

class vehicledelete(GenericAPIView):
    def post(self, request):
        id = request.data.get('vehicleid')
        obj = Vehicle.objects.filter(id=id, isActive=True).first()

        if not obj:
            return Response({"data": '', "response": {"n": 0, "msg": "Vehicle not found", "status": "error"}})

        serializer = VehicleSerializer(obj, data={'isActive': False}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "response": {"n": 1, "msg": "Vehicle deleted", "status": "success"}})

        first_key, first_value = next(iter(serializer.errors.items()))
        return Response({"data": serializer.errors, "response": {"n": 0, "msg": first_key+' : '+first_value[0], "status": "error"}})

class addlogisticsorder(GenericAPIView):
    def post(self, request):
        data = {
            'source': request.data.get('source'),
            'destination': request.data.get('destination'),
            'vehicle': request.data.get('vehicle'),
            'status': request.data.get('status', 'pending')
        }

        if not data['source'] or not data['destination']:
            return Response({"data": {}, "response": {"n": 0, "msg": "Source & destination required", "status": "error"}})

        serializer = LogisticsOrderSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "response": {"n": 1, "msg": "Order created", "status": "success"}})

        first_key, first_value = next(iter(serializer.errors.items()))
        return Response({"data": serializer.errors, "response": {"n": 0, "msg": first_key+' : '+first_value[0], "status": "error"}})
class logisticsorderlist(GenericAPIView):
    def get(self, request):
        objs = LogisticsOrder.objects.filter(isActive=True).order_by('id')
        serializer = LogisticsOrderSerializer(objs, many=True)

        return Response({
            "data": serializer.data,
            "response": {"n": 1, "msg": "Order list", "status": "success"}
        })
class logisticsorder_list_pagination_api(GenericAPIView):
    pagination_class = CustomPagination

    def post(self, request):
        objs = LogisticsOrder.objects.filter(isActive=True).order_by('-id')

        search = request.data.get('search')
        if search:
            objs = objs.filter(
                Q(source__icontains=search) |
                Q(destination__icontains=search) |
                Q(vehicle__icontains=search)
            )

        page = self.paginate_queryset(objs)
        serializer = LogisticsOrderSerializer(page, many=True)

        return self.get_paginated_response(serializer.data)
class logisticsorderupdate(GenericAPIView):
    def post(self, request):
        id = request.data.get('orderid')
        obj = LogisticsOrder.objects.filter(id=id, isActive=True).first()

        if not obj:
            return Response({"data": '', "response": {"n": 0, "msg": "Order not found", "status": "error"}})

        serializer = LogisticsOrderSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "response": {"n": 1, "msg": "Order updated", "status": "success"}})

        first_key, first_value = next(iter(serializer.errors.items()))
        return Response({"data": serializer.errors, "response": {"n": 0, "msg": first_key+' : '+first_value[0], "status": "error"}})

class logisticsorderbyid(GenericAPIView):
    def post(self, request):
        id = request.data.get('orderid')
        obj = LogisticsOrder.objects.filter(id=id, isActive=True).first()

        if obj:
            serializer = LogisticsOrderSerializer(obj)
            return Response({"data": serializer.data, "response": {"n": 1, "msg": "Order found", "status": "success"}})

        return Response({"data": '', "response": {"n": 0, "msg": "Order not found", "status": "error"}})

class logisticsorderdelete(GenericAPIView):
    def post(self, request):
        id = request.data.get('orderid')
        obj = LogisticsOrder.objects.filter(id=id, isActive=True).first()

        if not obj:
            return Response({"data": '', "response": {"n": 0, "msg": "Order not found", "status": "error"}})

        serializer = LogisticsOrderSerializer(obj, data={'isActive': False}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "response": {"n": 1, "msg": "Order deleted", "status": "success"}})

        first_key, first_value = next(iter(serializer.errors.items()))
        return Response({"data": serializer.errors, "response": {"n": 0, "msg": first_key+' : '+first_value[0], "status": "error"}})

class adddelivery(GenericAPIView):
    def post(self, request):
        data = {
            'order': request.data.get('order'),
            'agent': request.data.get('agent'),
            'status': request.data.get('status', 'assigned'),
            'delivered_at': request.data.get('delivered_at')
        }

        serializer = DeliverySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "response": {"n": 1, "msg": "Delivery created", "status": "success"}})

        first_key, first_value = next(iter(serializer.errors.items()))
        return Response({"data": serializer.errors, "response": {"n": 0, "msg": first_key+' : '+first_value[0], "status": "error"}})

class deliverylist(GenericAPIView):
    def get(self, request):
        objs = Delivery.objects.filter(isActive=True).order_by('id')
        serializer = DeliverySerializer(objs, many=True)

        return Response({
            "data": serializer.data,
            "response": {"n": 1, "msg": "Delivery list", "status": "success"}
        })

class delivery_list_pagination_api(GenericAPIView):
    pagination_class = CustomPagination

    def post(self, request):
        objs = Delivery.objects.filter(isActive=True).order_by('-id')

        search = request.data.get('search')
        if search:
            objs = objs.filter(
                Q(order__icontains=search) |
                Q(agent__icontains=search) |
                Q(status__icontains=search)
            )

        page = self.paginate_queryset(objs)
        serializer = DeliverySerializer(page, many=True)

        return self.get_paginated_response(serializer.data)
class deliveryupdate(GenericAPIView):
    def post(self, request):
        id = request.data.get('deliveryid')
        obj = Delivery.objects.filter(id=id, isActive=True).first()

        if not obj:
            return Response({"data": '', "response": {"n": 0, "msg": "Delivery not found", "status": "error"}})

        serializer = DeliverySerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "response": {"n": 1, "msg": "Delivery updated", "status": "success"}})

        first_key, first_value = next(iter(serializer.errors.items()))
        return Response({"data": serializer.errors, "response": {"n": 0, "msg": first_key+' : '+first_value[0], "status": "error"}})
class deliverybyid(GenericAPIView):
    def post(self, request):
        id = request.data.get('deliveryid')
        obj = Delivery.objects.filter(id=id, isActive=True).first()

        if obj:
            serializer = DeliverySerializer(obj)
            return Response({"data": serializer.data, "response": {"n": 1, "msg": "Delivery found", "status": "success"}})

        return Response({"data": '', "response": {"n": 0, "msg": "Delivery not found", "status": "error"}})

class deliverydelete(GenericAPIView):
    def post(self, request):
        id = request.data.get('deliveryid')
        obj = Delivery.objects.filter(id=id, isActive=True).first()

        if not obj:
            return Response({"data": '', "response": {"n": 0, "msg": "Delivery not found", "status": "error"}})

        serializer = DeliverySerializer(obj, data={'isActive': False}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "response": {"n": 1, "msg": "Delivery deleted", "status": "success"}})

        first_key, first_value = next(iter(serializer.errors.items()))
        return Response({"data": serializer.errors, "response": {"n": 0, "msg": first_key+' : '+first_value[0], "status": "error"}})






















