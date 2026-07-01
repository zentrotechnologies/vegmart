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
import math
from helpers.custom_functions import *
from Procurement.models import *
from Procurement.serializers import *
# Create your views here.
class addcategory(GenericAPIView):
    def post(self, request):
        data = {}
        data['name'] = str(request.data.get('name')).lower()

        if not data['name']:
            return Response({"data": {}, "response": {"n": 0, "msg": "Please provide category name", "status": "error"}})

        exist = Category.objects.filter(name=data['name'], isActive=True).first()
        if exist:
            return Response({"data": {}, "response": {"n": 0, "msg": "Category already exists", "status": "error"}})

        serializer = CategorySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "response": {"n": 1, "msg": "Category added successfully", "status": "success"}})
        
        first_key, first_value = next(iter(serializer.errors.items()))
        return Response({"data": serializer.errors, "response": {"n": 0, "msg": first_key + ' : ' + first_value[0], "status": "error"}})
    
class categorylist(GenericAPIView):
    def get(self, request):
        objs = Category.objects.filter(isActive=True).order_by('id')
        serializer = CategorySerializer(objs, many=True)

        return Response({
            "data": serializer.data,
            "response": {"n": 1, "msg": "Category list", "status": "success"}
        })
    
class category_list_pagination_api(GenericAPIView):
    pagination_class = CustomPagination

    def post(self, request):
        objs = Category.objects.filter(isActive=True).order_by('-id')

        search = request.data.get('search')
        if search:
            objs = objs.filter(name__icontains=search)

        page = self.paginate_queryset(objs)
        serializer = CategorySerializer(page, many=True)

        return self.get_paginated_response(serializer.data)
    
class categoryupdate(GenericAPIView):
    def post(self, request):
        id = request.data.get('categoryid')
        obj = Category.objects.filter(id=id, isActive=True).first()

        if not obj:
            return Response({"data": '', "response": {"n": 0, "msg": "Category not found", "status": "error"}})

        name = str(request.data.get('name')).lower()

        if not name:
            return Response({"data": {}, "response": {"n": 0, "msg": "Please provide category name", "status": "error"}})

        if Category.objects.filter(name=name, isActive=True).exclude(id=id).exists():
            return Response({"data": '', "response": {"n": 0, "msg": "Category already exists", "status": "error"}})

        serializer = CategorySerializer(obj, data={'name': name}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "response": {"n": 1, "msg": "Category updated", "status": "success"}})

        first_key, first_value = next(iter(serializer.errors.items()))
        return Response({"data": serializer.errors, "response": {"n": 0, "msg": first_key + ' : ' + first_value[0], "status": "error"}})
    
class categorybyid(GenericAPIView):
    def post(self, request):
        id = request.data.get('categoryid')
        obj = Category.objects.filter(id=id, isActive=True).first()

        if obj:
            serializer = CategorySerializer(obj)
            return Response({"data": serializer.data, "response": {"n": 1, "msg": "Category found", "status": "success"}})

        return Response({"data": '', "response": {"n": 0, "msg": "Category not found", "status": "error"}})
    

class categorydelete(GenericAPIView):
    def post(self, request):
        id = request.data.get('categoryid')
        obj = Category.objects.filter(id=id, isActive=True).first()

        if not obj:
            return Response({"data": '', "response": {"n": 0, "msg": "Category not found", "status": "error"}})

        serializer = CategorySerializer(obj, data={'isActive': False}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "response": {"n": 1, "msg": "Category deleted", "status": "success"}})

        first_key, first_value = next(iter(serializer.errors.items()))
        return Response({"data": serializer.errors, "response": {"n": 0, "msg": first_key + ' : ' + first_value[0], "status": "error"}})
    
class addsubcategory(GenericAPIView):
    def post(self, request):
        data = {}
        data['name'] = str(request.data.get('name')).lower()
        data['category'] = str(request.data.get('category')).lower()

        if not data['name'] or not data['category']:
            return Response({"data": {}, "response": {"n": 0, "msg": "Name & category required", "status": "error"}})

        exist = SubCategory.objects.filter(
            name=data['name'], category=data['category'], isActive=True
        ).first()

        if exist:
            return Response({"data": {}, "response": {"n": 0, "msg": "SubCategory exists", "status": "error"}})

        serializer = SubCategorySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "response": {"n": 1, "msg": "SubCategory added", "status": "success"}})

        first_key, first_value = next(iter(serializer.errors.items()))
        return Response({"data": serializer.errors, "response": {"n": 0, "msg": first_key + ' : ' + first_value[0], "status": "error"}})
    


class subcategorylist(GenericAPIView):
    def get(self, request):
        print("req",request.data)
        objs = SubCategory.objects.filter(isActive=True).order_by('id')
        serializer = SubCategorySerializer(objs, many=True)

        return Response({
            "data": serializer.data,
            "response": {"n": 1, "msg": "SubCategory list", "status": "success"}
        })
    def post(self, request):
        print("req",request.data)
        objs = SubCategory.objects.filter(isActive=True).order_by('id')
        category=request.data.get('category')
        if category is not None and category !='':
            objs=objs.filter(category=category)
        serializer = SubCategorySerializer(objs, many=True)

        return Response({
            "data": serializer.data,
            "response": {"n": 1, "msg": "SubCategory list", "status": "success"}
        })

class subcategory_list_pagination_api(GenericAPIView):
    pagination_class = CustomPagination

    def post(self, request):
        objs = SubCategory.objects.filter(isActive=True).order_by('-id')

        search = request.data.get('search')
        if search:
            objs = objs.filter(
                Q(name__icontains=search) | Q(category__icontains=search)
            )

        page = self.paginate_queryset(objs)
        serializer = CustomSubCategorySerializer(page, many=True)

        return self.get_paginated_response(serializer.data)
    

class subcategoryupdate(GenericAPIView):
    def post(self, request):
        id = request.data.get('subcategoryid')
        obj = SubCategory.objects.filter(id=id, isActive=True).first()

        if not obj:
            return Response({"data": '', "response": {"n": 0, "msg": "Not found", "status": "error"}})

        data = {
            'name': str(request.data.get('name')).lower(),
            'category': str(request.data.get('category')).lower()
        }

        serializer = SubCategorySerializer(obj, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "response": {"n": 1, "msg": "Updated", "status": "success"}})

        first_key, first_value = next(iter(serializer.errors.items()))
        return Response({"data": serializer.errors, "response": {"n": 0, "msg": first_key + ' : ' + first_value[0], "status": "error"}})

class subcategorybyid(GenericAPIView):
    def post(self, request):
        id = request.data.get('subcategoryid')
        obj = SubCategory.objects.filter(id=id, isActive=True).first()

        if obj:
            serializer = SubCategorySerializer(obj)
            return Response({"data": serializer.data, "response": {"n": 1, "msg": "Found", "status": "success"}})

        return Response({"data": '', "response": {"n": 0, "msg": "Not found", "status": "error"}})

class subcategorydelete(GenericAPIView):
    def post(self, request):
        id = request.data.get('subcategoryid')
        obj = SubCategory.objects.filter(id=id, isActive=True).first()

        if not obj:
            return Response({"data": '', "response": {"n": 0, "msg": "Not found", "status": "error"}})

        serializer = SubCategorySerializer(obj, data={'isActive': False}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "response": {"n": 1, "msg": "Deleted", "status": "success"}})

        first_key, first_value = next(iter(serializer.errors.items()))
        return Response({"data": serializer.errors, "response": {"n": 0, "msg": first_key + ' : ' + first_value[0], "status": "error"}})


class addproduct(GenericAPIView):

    def post(self, request):

        # 🔹 PRODUCT DATA
        print("request.data",request.data)
        data = {
            'name': str(request.data.get('name')).lower(),
            'sku': str(request.data.get('sku')).upper(),
            'hsn_code': request.data.get('hsn_code'),
            'category': str(request.data.get('category')).lower(),
            'sub_category': str(request.data.get('sub_category')).lower(),
            'unit': str(request.data.get('unit')).lower(),
            'brand': str(request.data.get('brand')).lower()
        }

        # 🔹 VALIDATION
        if not data['name'] or not data['sku']:
            return Response({"data": {}, "response": {"n": 0, "msg": "Name & SKU required", "status": "error"}})

        if Product.objects.filter(sku=data['sku'], isActive=True).exists():
            return Response({"data": {}, "response": {"n": 0, "msg": "SKU already exists", "status": "error"}})

        serializer = ProductSerializer(data=data)

        if serializer.is_valid():
            product = serializer.save()

            # 🔥 HANDLE VARIANTS (MULTIPART FORM)
            i = 0
            created = 0

            while True:
                pack_size = request.data.get(f'variants[{i}][pack_size]')
                if not pack_size:
                    break

                # 🔹 SAFE FLOAT CONVERTER
                def to_float(val, default=0):
                    try:
                        if val in ["", None]:
                            return default
                        return float(val)
                    except:
                        return default
                image = request.FILES.get(f'variants[{i}][image]')
                image_url = request.data.get(f'variants[{i}][image_url]')
                ProductVariant.objects.create(
                    product=str(product.id),
                    pack_size=pack_size,
                    pack_type=request.data.get(f'variants[{i}][pack_type]'),
                    fat=to_float(request.data.get(f'variants[{i}][fat]'), None),
                    snf=to_float(request.data.get(f'variants[{i}][snf]'), None),
                    gst_rate=to_float(request.data.get(f'variants[{i}][gst_rate]')),
                    mrp=to_float(request.data.get(f'variants[{i}][mrp]')),
                    b2b_price=to_float(request.data.get(f'variants[{i}][b2b_price]')),
                    image=image if image else image_url
                )

                created += 1
                i += 1

            return Response({
                "data": serializer.data,
                "response": {
                    "n": 1,
                    "msg": f"Product added with {created} variants",
                    "status": "success"
                }
            })

        # 🔹 ERROR HANDLING
        first_key, first_value = next(iter(serializer.errors.items()))
        return Response({
            "data": serializer.errors,
            "response": {"n": 0, "msg": first_key + ' : ' + first_value[0], "status": "error"}
        })
class productlist(GenericAPIView):
    def get(self, request):
        product_ids=list(ProductVariant.objects.filter(isActive=True).values_list("product",flat=True))
        objs = Product.objects.filter(id__in=product_ids,isActive=True).order_by('id')
        serializer = ProductSerializer(objs, many=True)

        return Response({
            "data": serializer.data,
            "response": {"n": 1, "msg": "Product list", "status": "success"}
        })
class procurementreadyproductlist(GenericAPIView):
    def get(self, request):
        product_ids=list(ProductVariant.objects.filter(isActive=True).order_by('product').distinct('product').values_list('product',flat=True))
        
        objs = Product.objects.filter(id__in=product_ids,isActive=True).order_by('id')
        serializer = CustomProductSerializer(objs, many=True)

        return Response({
            "data": serializer.data,
            "response": {"n": 1, "msg": "Product list", "status": "success"}
        })
        
class productionreadyproductlist(GenericAPIView):
    def get(self, request):
        product_ids=list(ProductVariant.objects.filter(isActive=True).order_by('product').distinct('product').values_list('product',flat=True))
        
        objs = Product.objects.filter(id__in=product_ids,isActive=True).order_by('id')
        serializer = CustomProductSerializer(objs, many=True)

        return Response({
            "data": serializer.data,
            "response": {"n": 1, "msg": "Product list", "status": "success"}
        })
        
        
class product_list_pagination_api(GenericAPIView):
    pagination_class = CustomPagination

    def post(self, request):
        objs = Product.objects.filter(isActive=True).order_by('-id')

        search = request.data.get('search')
        if search:
            objs = objs.filter(
                Q(name__icontains=search) |
                Q(sku__icontains=search) |
                Q(category__icontains=search) |
                Q(sub_category__icontains=search) |
                Q(brand__icontains=search)
            )

        page = self.paginate_queryset(objs)
        serializer = ProductSerializer(page, many=True)

        return self.get_paginated_response(serializer.data)

class productupdate(GenericAPIView):

    def post(self, request):
        product_id = request.data.get('productid')
        obj = Product.objects.filter(id=product_id, isActive=True).first()

        if not obj:
            return Response({
                "data": '',
                "response": {"n": 0, "msg": "Product not found", "status": "error"}
            })

        # 🔹 PRODUCT DATA
        data = {
            'name': str(request.data.get('name')).lower(),
            'sku': str(request.data.get('sku')).upper(),
            'hsn_code': request.data.get('hsn_code'),
            'category': str(request.data.get('category')).lower(),
            'sub_category': str(request.data.get('sub_category')).lower(),
            'unit': str(request.data.get('unit')).lower(),
            'brand': str(request.data.get('brand')).lower()
        }

        # 🔹 SKU CHECK
        if Product.objects.filter(sku=data['sku'], isActive=True).exclude(id=product_id).exists():
            return Response({
                "data": '',
                "response": {"n": 0, "msg": "SKU already exists", "status": "error"}
            })

        serializer = ProductSerializer(obj, data=data, partial=True)

        if serializer.is_valid():
            product = serializer.save()

            # 🔥 DELETE OLD VARIANTS
            ProductVariant.objects.filter(product=str(product.id)).delete()

            # 🔥 SAFE FLOAT (FIXED)
            def to_float(val, default=None):
                try:
                    if val in ["", None, "nan"]:
                        return default
                    val = float(val)
                    if math.isnan(val) or math.isinf(val):
                        return default
                    return val
                except:
                    return default

            # 🔥 HANDLE VARIANTS
            i = 0
            created = 0

            while True:
                pack_size = request.data.get(f'variants[{i}][pack_size]')
                if not pack_size:
                    break

                image = request.FILES.get(f'variants[{i}][image]')
                image_url = request.data.get(f'variants[{i}][image_url]')

                # ✅ IMAGE FIX
                if image:
                    final_image = image
                elif image_url:
                    final_image = image_url.split('/media/')[-1]
                else:
                    final_image = None

                ProductVariant.objects.create(
                    product=str(product.id),
                    pack_size=pack_size,
                    pack_type=request.data.get(f'variants[{i}][pack_type]'),
                    fat=to_float(request.data.get(f'variants[{i}][fat]')),
                    snf=to_float(request.data.get(f'variants[{i}][snf]')),
                    gst_rate=to_float(request.data.get(f'variants[{i}][gst_rate]'), 0),
                    mrp=to_float(request.data.get(f'variants[{i}][mrp]'), 0),
                    b2b_price=to_float(request.data.get(f'variants[{i}][b2b_price]'), 0),
                    image=final_image
                )

                created += 1
                i += 1

            return Response({
                "data": serializer.data,
                "response": {
                    "n": 1,
                    "msg": f"Product updated with {created} variants",
                    "status": "success"
                }
            })

        first_key, first_value = next(iter(serializer.errors.items()))
        return Response({
            "data": serializer.errors,
            "response": {
                "n": 0,
                "msg": first_key + ' : ' + first_value[0],
                "status": "error"
            }
        })
    
class productbyid(GenericAPIView):
    def post(self, request):
        id = request.data.get('productid')
        obj = Product.objects.filter(id=id, isActive=True).first()

        if obj:
            serializer = ProductSerializer(obj)
            return Response({"data": serializer.data, "response": {"n": 1, "msg": "Product found", "status": "success"}})

        return Response({"data": '', "response": {"n": 0, "msg": "Product not found", "status": "error"}})

class productdelete(GenericAPIView):
    def post(self, request):
        id = request.data.get('productid')
        obj = Product.objects.filter(id=id, isActive=True).first()

        if not obj:
            return Response({"data": '', "response": {"n": 0, "msg": "Product not found", "status": "error"}})

        serializer = ProductSerializer(obj, data={'isActive': False}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "response": {"n": 1, "msg": "Product deleted", "status": "success"}})

        first_key, first_value = next(iter(serializer.errors.items()))
        return Response({"data": serializer.errors, "response": {"n": 0, "msg": first_key+' : '+first_value[0], "status": "error"}})

class addproductvariant(GenericAPIView):
    def post(self, request):
        data = {
            'product': str(request.data.get('product')).lower(),
            'pack_size': request.data.get('pack_size'),
            'pack_type': request.data.get('pack_type'),
            'fat': request.data.get('fat'),
            'snf': request.data.get('snf'),
            'gst_rate': request.data.get('gst_rate'),
            'mrp': request.data.get('mrp'),
            'b2b_price': request.data.get('b2b_price'),
        }

        if not data['product']:
            return Response({"data": {}, "response": {"n": 0, "msg": "Product required", "status": "error"}})

        serializer = ProductVariantSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "response": {"n": 1, "msg": "Variant added", "status": "success"}})

        first_key, first_value = next(iter(serializer.errors.items()))
        return Response({"data": serializer.errors, "response": {"n": 0, "msg": first_key+' : '+first_value[0], "status": "error"}})

class productvariantlist(GenericAPIView):
    def get(self, request):
        objs = ProductVariant.objects.filter(isActive=True).order_by('id')
        serializer = CustomProductVariantSerializer(objs, many=True)

        return Response({
            "data": serializer.data,
            "response": {"n": 1, "msg": "Variant list", "status": "success"}
        })
class getprocurementexpectedproductvariantlist(GenericAPIView):
    def post(self, request):
        procurement_id=request.data.get('procurement_id')
        if procurement_id is None or procurement_id =='':
            return Response({
            "data": [],
            "response": {"n": 0, "msg": "please provide procurement id", "status": "error"}
        })
        procurement_obj=ProcurementEntry.objects.filter(id=procurement_id,isActive=True).first()
        if procurement_obj is None:
            return Response({
            "data": [],
            "response": {"n": 0, "msg": "procurement obj not found", "status": "error"}
        })
        procurement_products_base_query=ProcurementProducts.objects.filter(procurement=procurement_obj.id).order_by('product_id').distinct('product_id')
        procurement_product_ids=list(procurement_products_base_query.values_list('product_id',flat=True))
        procurement_products_serializer=CustomProcurementProductsSerializer(procurement_products_base_query,many=True)
       

        objs = ProductVariant.objects.filter(isActive=True,product__in=procurement_product_ids).order_by('id')
        if objs.exists():
            serializer = CustomProductVariantSerializer(objs, many=True)
            return Response({
                "data": {"variants":serializer.data,"products":procurement_products_serializer.data},
                "response": {"n": 1, "msg": "Variant list", "status": "success"}
            })
        else:
            return Response({
            "data": [],
            "response": {"n": 0, "msg": "procurement variants not found", "status": "error"}
        })


class getprocurementexpectedrawproductlist(GenericAPIView):
    def post(self, request):
        procurement_id=request.data.get('procurement_id')
        if procurement_id is None or procurement_id =='':
            return Response({
            "data": [],
            "response": {"n": 0, "msg": "please provide procurement id", "status": "error"}
        })
        procurement_obj=ProcurementEntry.objects.filter(id=procurement_id,isActive=True).first()
        if procurement_obj is None:
            return Response({
            "data": [],
            "response": {"n": 0, "msg": "procurement obj not found", "status": "error"}
        })


        objs = ProcurementRawmaterial.objects.filter(isActive=True,procurement=procurement_id).order_by('id')
        if objs.exists():
            serializer = CustomProcurementRawmaterialSerializer(objs, many=True)
            return Response({
                "data": {"raw_materials":serializer.data,},
                "response": {"n": 1, "msg": "Variant list", "status": "success"}
            })
        else:
            return Response({
            "data": [],
            "response": {"n": 0, "msg": "procurement variants not found", "status": "error"}
        })








class productvariant_list_pagination_api(GenericAPIView):
    pagination_class = CustomPagination

    def post(self, request):
        objs = ProductVariant.objects.filter(isActive=True).order_by('-id')

        search = request.data.get('search')
        if search:
            objs = objs.filter(
                Q(product__icontains=search) |
                Q(pack_size__icontains=search) |
                Q(pack_type__icontains=search)
            )

        page = self.paginate_queryset(objs)
        serializer = CustomProductVariantSerializer(page, many=True)

        return self.get_paginated_response(serializer.data)


class productvariantupdate(GenericAPIView):
    def post(self, request):
        id = request.data.get('variantid')
        obj = ProductVariant.objects.filter(id=id, isActive=True).first()

        if not obj:
            return Response({"data": '', "response": {"n": 0, "msg": "Variant not found", "status": "error"}})

        data = request.data

        serializer = ProductVariantSerializer(obj, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "response": {"n": 1, "msg": "Variant updated", "status": "success"}})

        first_key, first_value = next(iter(serializer.errors.items()))
        return Response({"data": serializer.errors, "response": {"n": 0, "msg": first_key+' : '+first_value[0], "status": "error"}})

class productvariantbyid(GenericAPIView):
    def post(self, request):
        id = request.data.get('variantid')
        obj = ProductVariant.objects.filter(id=id, isActive=True).first()

        if obj:
            serializer = ProductVariantSerializer(obj)
            return Response({"data": serializer.data, "response": {"n": 1, "msg": "Variant found", "status": "success"}})

        return Response({"data": '', "response": {"n": 0, "msg": "Variant not found", "status": "error"}})

class productvariantdelete(GenericAPIView):
    def post(self, request):
        id = request.data.get('variantid')
        obj = ProductVariant.objects.filter(id=id, isActive=True).first()

        if not obj:
            return Response({"data": '', "response": {"n": 0, "msg": "Variant not found", "status": "error"}})

        serializer = ProductVariantSerializer(obj, data={'isActive': False}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "response": {"n": 1, "msg": "Variant deleted", "status": "success"}})

        first_key, first_value = next(iter(serializer.errors.items()))
        return Response({"data": serializer.errors, "response": {"n": 0, "msg": first_key+' : '+first_value[0], "status": "error"}})

class productvariantbyproduct(GenericAPIView):
    def post(self, request):
        productid = request.data.get('productid')

        objs = ProductVariant.objects.filter(product=str(productid), isActive=True)

        data = []
        for obj in objs:
            data.append({
                "id": obj.id,
                "pack_size": obj.pack_size,
                "pack_type": obj.pack_type,
                "mrp": obj.mrp,
                "b2b_price": obj.b2b_price,
                "image_url": hosturl+"/media/"+str(obj.image),
                "fat": obj.fat,
                "snf": obj.snf,
                "gst_rate": obj.gst_rate,
                "product": obj.product,

            })

        return Response({
            "data": data,
            "response": {"n": 1, "msg": "Variant list", "status": "success"}
        })

class unitlist(GenericAPIView):
    def get(self, request):
        objs = UnitMaster.objects.filter(isActive=True).order_by('id')
        serializer = UnitMasterSerializer(objs, many=True)

        return Response({
            "data": serializer.data,
            "response": {"n": 1, "msg": "Unit Master list", "status": "success"}
        })
    