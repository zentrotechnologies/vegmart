
from .models import *
from rest_framework import serializers

class BatchOutputSerializer(serializers.ModelSerializer):
    
    class Meta:
        model= BatchOutput
        fields='__all__'
class ProcessingBatchSerializer(serializers.ModelSerializer):
    
    class Meta:
        model= ProcessingBatch
        fields='__all__'
