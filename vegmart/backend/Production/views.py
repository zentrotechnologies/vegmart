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
class addprocessingbatch(GenericAPIView):
    def post(self, request):
        batch_number = request.data.get('batch_number')
        input_qty = float(request.data.get('input_quantity') or 0)
        output_qty = float(request.data.get('output_quantity') or 0)

        if ProcessingBatch.objects.filter(batch_number=batch_number).exists():
            return Response({"data": {}, "response": {"n": 0, "msg": "Batch exists", "status": "error"}})

        batch = ProcessingBatch.objects.create(
            batch_number=batch_number,
            input_quantity=input_qty,
            output_quantity=output_qty
        )

        return Response({
            "data": {"batch_id": batch.id},
            "response": {"n": 1, "msg": "Batch created", "status": "success"}
        })
    
class addbatchoutput(GenericAPIView):
    def post(self, request):
        batch_id = request.data.get('batch_id')
        outputs = request.data.get('outputs')  # list

        for item in outputs:
            BatchOutput.objects.create(
                batch=batch_id,
                product_variant=item.get('product_variant'),
                quantity=item.get('quantity')
            )

        return Response({
            "data": {},
            "response": {"n": 1, "msg": "Batch output saved", "status": "success"}
        })

class processingbatchlist(GenericAPIView):
    def get(self, request):
        objs = ProcessingBatch.objects.filter(isActive=True).order_by('-id')
        serializer = ProcessingBatchSerializer(objs, many=True)

        return Response({
            "data": serializer.data,
            "response": {"n": 1, "msg": "Production batches", "status": "success"}
        })
    
class batchdetails(GenericAPIView):
    def post(self, request):
        batch_id = request.data.get('batch_id')

        batch = ProcessingBatch.objects.filter(id=batch_id).first()
        outputs = BatchOutput.objects.filter(batch=str(batch_id))

        return Response({
            "data": {
                "batch": ProcessingBatchSerializer(batch).data,
                "outputs": BatchOutputSerializer(outputs, many=True).data
            },
            "response": {"n": 1, "msg": "Batch details", "status": "success"}
        })


















