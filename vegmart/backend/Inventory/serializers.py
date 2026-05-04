
from .models import *
from Masters.models import *
from Masters.serializers import *
from rest_framework import serializers

class WarehouseSerializer(serializers.ModelSerializer):
    
    class Meta:
        model= Warehouse
        fields='__all__'


class BatchSerializer(serializers.ModelSerializer):
    
    class Meta:
        model= Batch
        fields='__all__'

class InventorySerializer(serializers.ModelSerializer):
    
    class Meta:
        model= Inventory
        fields='__all__'

class CustomInventorySerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()
    def get_product_name(self, obj):
        obj_id = obj.product_variant
        
        if obj_id is not None and obj_id !='' and obj_id !='None':
            try:
                obj = ProductVariant.objects.filter(id=obj_id).first()
                if obj is not None:
                   ser=CustomProductVariantSerializer(obj)
                   return ser.data['product_name']
                else:
                    return None
            except ProductVariant.DoesNotExist:
                return None
        return None
    


    product_unit = serializers.SerializerMethodField()
    def get_product_unit(self, obj):
        obj_id = obj.product_variant
        
        if obj_id is not None and obj_id !='' and obj_id !='None':
            try:
                obj = ProductVariant.objects.filter(id=obj_id).first()
                if obj is not None:
                   ser=CustomProductVariantSerializer(obj)
                   return ser.data['product_unit']
                else:
                    return None
            except ProductVariant.DoesNotExist:
                return None
        return None
    
    pack_size = serializers.SerializerMethodField()
    def get_pack_size(self, obj):
        obj_id = obj.product_variant
        
        if obj_id is not None and obj_id !='' and obj_id !='None':
            try:
                obj = ProductVariant.objects.filter(id=obj_id).first()
                if obj is not None:
                   ser=CustomProductVariantSerializer(obj)
                   return ser.data['pack_size']
                else:
                    return None
            except ProductVariant.DoesNotExist:
                return None
        return None
    pack_type = serializers.SerializerMethodField()
    def get_pack_type(self, obj):
        obj_id = obj.product_variant
        
        if obj_id is not None and obj_id !='' and obj_id !='None':
            try:
                obj = ProductVariant.objects.filter(id=obj_id).first()
                if obj is not None:
                   ser=CustomProductVariantSerializer(obj)
                   return ser.data['pack_type']
                else:
                    return None
            except ProductVariant.DoesNotExist:
                return None
        return None
    class Meta:
        model= Inventory
        fields='__all__'