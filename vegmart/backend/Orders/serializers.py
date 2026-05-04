
from .models import *
from rest_framework import serializers
from Customers.models import *
from Customers.serializers import *
from Masters.models import *
class OrderSerializer(serializers.ModelSerializer):
    
    class Meta:
        model= Order
        fields='__all__'


class CustomOrderSerializer(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField()
    def get_customer_name(self, obj):
        obj_id = obj.customer_id
        
        if obj_id is not None and obj_id !='' and obj_id !='None':
            try:
                obj = Customer.objects.filter(id=obj_id).first()
                if obj is not None:
                   return obj.name
                else:
                    return None
            except Customer.DoesNotExist:
                return None
        return None
    

    customer_details = serializers.SerializerMethodField()
    def get_customer_details(self, obj):
        obj_id = obj.customer_id
        
        if obj_id is not None and obj_id !='' and obj_id !='None':
            try:
                obj = Customer.objects.filter(id=obj_id).first()
                if obj is not None:
                   ser=CustomerSerializer(obj)
                   return ser.data
                else:
                    return None
            except Customer.DoesNotExist:
                return None
        return None
    


    class Meta:
        model= Order
        fields='__all__'
        
class OrderItemSerializer(serializers.ModelSerializer):
    
    class Meta:
        model= OrderItem
        fields='__all__'
class CustomOrderItemSerializer(serializers.ModelSerializer):
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
    
    product_hsn_code = serializers.SerializerMethodField()
    def get_product_hsn_code(self, obj):
        obj_id = obj.product
        
        if obj_id is not None and obj_id !='' and obj_id !='None':
            try:
                obj = Product.objects.filter(id=obj_id).first()
                if obj is not None:
                   return obj.hsn_code
                else:
                    return None
            except Product.DoesNotExist:
                return None
        return None
    
    pack_size = serializers.SerializerMethodField()
    def get_pack_size(self, obj):
        obj_id = obj.product_variant
        
        if obj_id is not None and obj_id !='' and obj_id !='None':
            try:
                obj = ProductVariant.objects.filter(id=obj_id).first()
                if obj is not None:
                   return obj.pack_size
                else:
                    return None
            except ProductVariant.DoesNotExist:
                return None
        return None


    class Meta:
        model= OrderItem
        fields='__all__'
class CustomerPricingSerializer(serializers.ModelSerializer):
    
    class Meta:
        model= CustomerPricing
        fields='__all__'


class PaymentSerializer(serializers.ModelSerializer):
    
    class Meta:
        model= Payment
        fields='__all__'







