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

class addwarehouse(GenericAPIView):
    def post(self, request):
        data = {
            'name': str(request.data.get('name')).lower(),
            'location': request.data.get('location'),
        }

        if not data['name']:
            return Response({"data": {}, "response": {"n": 0, "msg": "Warehouse name required", "status": "error"}})

        exist = Warehouse.objects.filter(name=data['name'], isActive=True).first()
        if exist:
            return Response({"data": {}, "response": {"n": 0, "msg": "Warehouse already exists", "status": "error"}})

        serializer = WarehouseSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "response": {"n": 1, "msg": "Warehouse added", "status": "success"}})

        first_key, first_value = next(iter(serializer.errors.items()))
        return Response({"data": serializer.errors, "response": {"n": 0, "msg": first_key+' : '+first_value[0], "status": "error"}})

class warehouselist(GenericAPIView):
    def get(self, request):
        objs = Warehouse.objects.filter(isActive=True).order_by('id')
        serializer = WarehouseSerializer(objs, many=True)

        return Response({
            "data": serializer.data,
            "response": {"n": 1, "msg": "Warehouse list", "status": "success"}
        })
class warehouse_list_pagination_api(GenericAPIView):
    pagination_class = CustomPagination

    def post(self, request):
        objs = Warehouse.objects.filter(isActive=True).order_by('-id')

        search = request.data.get('search')
        if search:
            objs = objs.filter(
                Q(name__icontains=search) |
                Q(location__icontains=search)
            )

        page = self.paginate_queryset(objs)
        serializer = WarehouseSerializer(page, many=True)

        return self.get_paginated_response(serializer.data)

class warehouseupdate(GenericAPIView):
    def post(self, request):
        id = request.data.get('warehouseid')
        obj = Warehouse.objects.filter(id=id, isActive=True).first()

        if not obj:
            return Response({"data": '', "response": {"n": 0, "msg": "Warehouse not found", "status": "error"}})

        data = {
            'name': str(request.data.get('name')).lower(),
            'location': request.data.get('location'),
        }

        serializer = WarehouseSerializer(obj, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "response": {"n": 1, "msg": "Warehouse updated", "status": "success"}})

        first_key, first_value = next(iter(serializer.errors.items()))
        return Response({"data": serializer.errors, "response": {"n": 0, "msg": first_key+' : '+first_value[0], "status": "error"}})

class warehousebyid(GenericAPIView):
    def post(self, request):
        id = request.data.get('warehouseid')
        obj = Warehouse.objects.filter(id=id, isActive=True).first()

        if obj:
            serializer = WarehouseSerializer(obj)
            return Response({"data": serializer.data, "response": {"n": 1, "msg": "Warehouse found", "status": "success"}})

        return Response({"data": '', "response": {"n": 0, "msg": "Warehouse not found", "status": "error"}})
class warehousedelete(GenericAPIView):
    def post(self, request):
        id = request.data.get('warehouseid')
        obj = Warehouse.objects.filter(id=id, isActive=True).first()

        if not obj:
            return Response({"data": '', "response": {"n": 0, "msg": "Warehouse not found", "status": "error"}})

        serializer = WarehouseSerializer(obj, data={'isActive': False}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "response": {"n": 1, "msg": "Warehouse deleted", "status": "success"}})

        first_key, first_value = next(iter(serializer.errors.items()))
        return Response({"data": serializer.errors, "response": {"n": 0, "msg": first_key+' : '+first_value[0], "status": "error"}})

class addbatch(GenericAPIView):
    def post(self, request):
        data = {
            'batch_number': str(request.data.get('batch_number')).upper(),
            'product_variant': request.data.get('product_variant'),
            'expiry_date': request.data.get('expiry_date'),
            'quantity': request.data.get('quantity'),
        }

        if not data['batch_number']:
            return Response({"data": {}, "response": {"n": 0, "msg": "Batch number required", "status": "error"}})

        exist = Batch.objects.filter(batch_number=data['batch_number'], isActive=True).first()
        if exist:
            return Response({"data": {}, "response": {"n": 0, "msg": "Batch already exists", "status": "error"}})

        serializer = BatchSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "response": {"n": 1, "msg": "Batch added", "status": "success"}})

        first_key, first_value = next(iter(serializer.errors.items()))
        return Response({"data": serializer.errors, "response": {"n": 0, "msg": first_key+' : '+first_value[0], "status": "error"}})

class batchlist(GenericAPIView):
    def get(self, request):
        objs = Batch.objects.filter(isActive=True).order_by('id')
        serializer = BatchSerializer(objs, many=True)

        return Response({
            "data": serializer.data,
            "response": {"n": 1, "msg": "Batch list", "status": "success"}
        })

class batch_list_pagination_api(GenericAPIView):
    pagination_class = CustomPagination

    def post(self, request):
        objs = Batch.objects.filter(isActive=True).order_by('-id')

        search = request.data.get('search')
        if search:
            objs = objs.filter(
                Q(batch_number__icontains=search) |
                Q(product_variant__icontains=search)
            )

        page = self.paginate_queryset(objs)
        serializer = BatchSerializer(page, many=True)

        return self.get_paginated_response(serializer.data)

class batchupdate(GenericAPIView):
    def post(self, request):
        id = request.data.get('batchid')
        obj = Batch.objects.filter(id=id, isActive=True).first()

        if not obj:
            return Response({"data": '', "response": {"n": 0, "msg": "Batch not found", "status": "error"}})

        serializer = BatchSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "response": {"n": 1, "msg": "Batch updated", "status": "success"}})

        first_key, first_value = next(iter(serializer.errors.items()))
        return Response({"data": serializer.errors, "response": {"n": 0, "msg": first_key+' : '+first_value[0], "status": "error"}})

class batchbyid(GenericAPIView):
    def post(self, request):
        id = request.data.get('batchid')
        obj = Batch.objects.filter(id=id, isActive=True).first()

        if obj:
            serializer = BatchSerializer(obj)
            return Response({"data": serializer.data, "response": {"n": 1, "msg": "Batch found", "status": "success"}})

        return Response({"data": '', "response": {"n": 0, "msg": "Batch not found", "status": "error"}})

class batchdelete(GenericAPIView):
    def post(self, request):
        id = request.data.get('batchid')
        obj = Batch.objects.filter(id=id, isActive=True).first()

        if not obj:
            return Response({"data": '', "response": {"n": 0, "msg": "Batch not found", "status": "error"}})

        serializer = BatchSerializer(obj, data={'isActive': False}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "response": {"n": 1, "msg": "Batch deleted", "status": "success"}})

        first_key, first_value = next(iter(serializer.errors.items()))
        return Response({"data": serializer.errors, "response": {"n": 0, "msg": first_key+' : '+first_value[0], "status": "error"}})


class inventorylist(GenericAPIView):
    def get(self, request):
        objs = Inventory.objects.filter(isActive=True).order_by('-id')
        serializer = InventorySerializer(objs, many=True)

        return Response({
            "data": serializer.data,
            "response": {"n": 1, "msg": "Inventory list", "status": "success"}
        })

class inventory_list_pagination_api(GenericAPIView):
    pagination_class = CustomPagination

    def post(self, request):

        objs = Inventory.objects.filter(isActive=True,quantity__gte=1).order_by('-id')

        search = request.data.get('search')

        if search:
            objs = objs.filter(
                Q(product_variant__icontains=search) |
                Q(warehouse__icontains=search)
            )

        page = self.paginate_queryset(objs)
        serializer = CustomInventorySerializer(page, many=True)

        return self.get_paginated_response(serializer.data)

class inventoryupdate(GenericAPIView):

    def post(self, request):

        id = request.data.get('inventoryid')
        qty = request.data.get('quantity')

        obj = Inventory.objects.filter(id=id, isActive=True).first()

        if not obj:
            return Response({
                "response": {"n": 0, "msg": "Inventory not found", "status": "error"}
            })

        try:
            qty = float(qty)
        except:
            return Response({
                "response": {"n": 0, "msg": "Invalid quantity", "status": "error"}
            })

        obj.quantity = qty
        obj.save()

        return Response({
            "data": {},
            "response": {"n": 1, "msg": "Inventory updated", "status": "success"}
        })


class inventorydelete(GenericAPIView):

    def post(self, request):

        id = request.data.get('inventoryid')

        obj = Inventory.objects.filter(id=id, isActive=True).first()

        if not obj:
            return Response({
                "response": {"n": 0, "msg": "Inventory not found", "status": "error"}
            })



        obj.isActive = False
        obj.save()

        return Response({
            "data": {},
            "response": {"n": 1, "msg": "Inventory deleted successfully", "status": "success"}
        })


































