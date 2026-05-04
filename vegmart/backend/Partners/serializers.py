
from .models import *
from rest_framework import serializers

class DeliveryAgentSerializer(serializers.ModelSerializer):
    
    class Meta:
        model= DeliveryAgent
        fields='__all__'


class VendorSerializer(serializers.ModelSerializer):
    
    class Meta:
        model= Vendor
        fields='__all__'