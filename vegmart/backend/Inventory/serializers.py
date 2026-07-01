
from .models import *
from Masters.models import *
from Masters.serializers import *
from rest_framework import serializers
from Procurement.models import *
from Procurement.serializers import *
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
    
    
    stock_name = serializers.SerializerMethodField()
    def get_stock_name(self, obj):
        obj_id = obj.stock_id
        
        if obj_id is not None and obj_id !='' and obj_id !='None':
            try:
                if obj.inventory_type =='raw':
                    obj = RawProductMaster.objects.filter(id=obj_id).first()
                    if obj is not None:
                        return obj.name
                    else:
                        return None
                elif obj.inventory_type =='finished':
                    obj = Product.objects.filter(id=obj_id).first()
                    if obj is not None:
                        ser=CustomProductSerializer(obj)
                        return ser.data['name']
                    else:
                        return None
                else:
                    obj = ProductVariant.objects.filter(id=obj_id).first()
                    if obj is not None:
                        ser=CustomProductVariantSerializer(obj)
                        return ser.data['product_name']
                    else:
                        return None
            except ProductVariant.DoesNotExist:
                return None
        return None
    


    unit_name = serializers.SerializerMethodField()
    def get_unit_name(self, obj):
        obj_id = obj.unit
        
        if obj_id is not None and obj_id !='' and obj_id !='None':
            try:
                obj = UnitMaster.objects.filter(id=obj_id).first()
                if obj is not None:
                    return obj.short_name
                else:
                    return None
               
            except UnitMaster.DoesNotExist:
                return None
        return None
    
    
    
    pack_size = serializers.SerializerMethodField()
    def get_pack_size(self, obj):
        obj_id = obj.stock_id
        
        if obj_id is not None and obj_id !='' and obj_id !='None':
            try:
                if obj.inventory_type =='raw':
                    return None
                else:
                    
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
        obj_id = obj.stock_id
        if obj_id is not None and obj_id !='' and obj_id !='None':
            try:
                if obj.inventory_type =='raw':
                    return None
                else:
                    
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