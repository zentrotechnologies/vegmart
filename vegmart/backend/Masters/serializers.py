
from .models import *
from rest_framework import serializers

class CategorySerializer(serializers.ModelSerializer):
    
    class Meta:
        model= Category
        fields='__all__'

class SubCategorySerializer(serializers.ModelSerializer):
    
    class Meta:
        model= SubCategory
        fields='__all__'
class CustomSubCategorySerializer(serializers.ModelSerializer):
    category_name = serializers.SerializerMethodField()
    def get_category_name(self, obj):
        obj_id = obj.category
        
        if obj_id is not None and obj_id !='' and obj_id !='None':
            try:
                obj = Category.objects.filter(id=obj_id).first()
                if obj is not None:
                   return obj.name
                else:
                    return None
            except Category.DoesNotExist:
                return None
        return None
    

    class Meta:
        model= SubCategory
        fields='__all__'

class ProductSerializer(serializers.ModelSerializer):
    
    class Meta:
        model= Product
        fields='__all__'


class ProductVariantSerializer(serializers.ModelSerializer):
    
    class Meta:
        model= ProductVariant
        fields='__all__'



class CustomProductVariantSerializer(serializers.ModelSerializer):
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
    product_unit = serializers.SerializerMethodField()
    def get_product_unit(self, obj):
        obj_id = obj.product
        
        if obj_id is not None and obj_id !='' and obj_id !='None':
            try:
                obj = Product.objects.filter(id=obj_id).first()
                if obj is not None:
                   return obj.unit
                else:
                    return None
            except Product.DoesNotExist:
                return None
        return None


    class Meta:
        model= ProductVariant
        fields='__all__'