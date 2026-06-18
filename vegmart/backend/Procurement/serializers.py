
from .models import *
from rest_framework import serializers
from Masters.models import *
from Masters.serializers import *
from Partners.models import *
# class ProcurementItemSerializer(serializers.ModelSerializer):
    
#     class Meta:
#         model= ProcurementItem
#         fields='__all__'

class RawProductMasterSerializer(serializers.ModelSerializer):
    
    class Meta:
        model= RawProductMaster
        fields='__all__'


class CustomRawProductMasterSerializer(serializers.ModelSerializer):
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
    class Meta:
        model= RawProductMaster
        fields='__all__'
class ProcurementEntrySerializer(serializers.ModelSerializer):
    
    class Meta:
        model= ProcurementEntry
        fields='__all__'


class RecipeMasterSerializer(serializers.ModelSerializer):
    
    class Meta:
        model= RecipeMaster
        fields='__all__'

class CustomRecipeMasterSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()
    def get_product_name(self, obj):
        obj_id = obj.product
        
        if obj_id is not None and obj_id !='' and obj_id !='None':
            try:
                obj = Product.objects.filter(id=obj_id).first()
                if obj is not None:
                   return obj.name
                   
                else:
                    return None
            except Product.DoesNotExist:
                return None
        return None
    
    output_unit_name = serializers.SerializerMethodField()
    def get_output_unit_name(self, obj):
        obj_id = obj.output_unit
        
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

    class Meta:
        model= RecipeMaster
        fields='__all__'



# class CustomProcurementEntrySerializer(serializers.ModelSerializer):
    
    
#     product_names = serializers.SerializerMethodField()
#     def get_product_names(self, obj):
#         obj_id = obj.id
        
#         if obj_id is not None and obj_id !='' and obj_id !='None':
#             try:
#                 product_ids = list(ProcurementProducts.objects.filter(procurement=obj_id).exclude(product_id='undefined').values_list('product_id',flat=True))
#                 products_names=Product.objects.filter(id__in=product_ids,isActive=True).order_by('id').distinct('id').values_list('name',flat=True)                   
#                 return products_names
#             except ProcurementProducts.DoesNotExist:
#                 return None
#         return None
    

#     supplier_name = serializers.SerializerMethodField()
#     def get_supplier_name(self, obj):
#         obj_id = obj.supplier_id
        
#         if obj_id is not None and obj_id !='' and obj_id !='None':
#             try:
#                 obj = Vendor.objects.filter(id=obj_id).first()
#                 if obj is not None:
#                    return obj.name
                   
#                 else:
#                     return None
#             except ProductVariant.DoesNotExist:
#                 return None
#         return None
    
#     class Meta:
#         model= ProcurementEntry
#         fields='__all__'
# class CustomProcurementItemSerializer(serializers.ModelSerializer):
#     procurement_item_name = serializers.SerializerMethodField()
#     def get_procurement_item_name(self, obj):
#         obj_id = obj.procurement_item_id
        
#         if obj_id is not None and obj_id !='' and obj_id !='None':
#             try:
#                 obj = RawProductMaster.objects.filter(id=obj_id).first()
#                 if obj is not None:
                   
#                    return obj.name
                   
#                 else:
#                     return None
#             except RawProductMaster.DoesNotExist:
#                 return None
#         return None
#     class Meta:
#         model= ProcurementItem
#         fields='__all__'

# class CustomProcurementProductsSerializer(serializers.ModelSerializer):
#     product_name = serializers.SerializerMethodField()
#     def get_product_name(self, obj):
#         obj_id = obj.product_id
        
#         if obj_id is not None and obj_id !='' and obj_id !='None':
#             try:
#                 obj = Product.objects.filter(id=obj_id).first()
#                 if obj is not None:
                   
#                    return obj.name
                   
#                 else:
#                     return None
#             except Product.DoesNotExist:
#                 return None
#         return None
    
#     product_unit = serializers.SerializerMethodField()
#     def get_product_unit(self, obj):
#         obj_id = obj.product_id
        
#         if obj_id is not None and obj_id !='' and obj_id !='None':
#             try:
#                 obj = Product.objects.filter(id=obj_id).first()
#                 if obj is not None:
#                    return obj.unit
                   
#                 else:
#                     return None
#             except Product.DoesNotExist:
#                 return None
#         return None
    



#     class Meta:
#         model= ProcurementProducts
#         fields='__all__'


