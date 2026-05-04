
from .models import *
from rest_framework import serializers

class CustomerSerializer(serializers.ModelSerializer):
    
    class Meta:
        model= Customer
        fields='__all__'