
from .models import *
from rest_framework import serializers
class VehicleSerializer(serializers.ModelSerializer):
    
    class Meta:
        model= Vehicle
        fields='__all__'
class LogisticsOrderSerializer(serializers.ModelSerializer):
    
    class Meta:
        model= LogisticsOrder
        fields='__all__'


class DeliverySerializer(serializers.ModelSerializer):
    
    class Meta:
        model= Delivery
        fields='__all__'
