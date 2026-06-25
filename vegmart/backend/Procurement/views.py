from django.shortcuts import render

# Create your views here.from rest_framework.response import Response
from rest_framework.authentication import (BaseAuthentication,
                                           get_authorization_header)
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from Masters.models import *
from django.contrib.auth import authenticate
from .models import *
from .serializers import *
from User.jwt import userJWTAuthentication
from django.template.loader import get_template, render_to_string
from django.core.mail import EmailMessage
from User.common import CustomPagination
from Inventory.models import Inventory
import json, datetime
from django.db.models import Sum,Q
from Orders.models import *
from django.db import transaction
from decimal import Decimal

class addprocuremententry(GenericAPIView):
    def post(self, request):
        print("request.data",request.data)
        supplier_id = request.data.get('supplier_id')
        item_id = request.data.get('item_id')

        quantity = float(request.data.get('quantity') or 0)
        rate = float(request.data.get('rate') or 0)

        fat = request.data.get('fat')
        snf = request.data.get('snf')

        paid_amount = float(request.data.get('paid_amount') or 0)

        if quantity <= 0:
            return Response({
                "response": {"n": 0, "msg": "Quantity must be > 0", "status": "error"}
            })

        total = quantity * rate
        credit_amount = total - paid_amount

        due_date = None
        if credit_amount > 0:
            due_date = datetime.date.today() + datetime.timedelta(days=7)
        unit = request.data.get('unit')
        order_id = request.data.get('order_id')
        if not unit:
            return Response({
                "response": {"n": 0, "msg": "Unit is required", "status": "error"}
            })
        entry = ProcurementEntry.objects.create(
            supplier_id=supplier_id,
            item_id=item_id,
            quantity=quantity,
            unit=request.data.get('unit') or 'liter',
            rate=rate,
            total=total,
            fat=fat,
            snf=snf,
            paid_amount=paid_amount,
            credit_amount=credit_amount,
            due_date=due_date,
            order_id=order_id
        )

        # 🔥 INVENTORY UPDATE (IMPORTANT)
        inv, created = Inventory.objects.get_or_create(
            stock_id=item_id,
            warehouse="default"
        )
        inv.quantity += quantity
        inv.save()

        return Response({
            "data": {"entry_id": entry.id},
            "response": {"n": 1, "msg": "Procurement entry added", "status": "success"}
        })

class procurementlist(GenericAPIView):
    def get(self, request):
        objs = ProcurementEntry.objects.filter(isActive=True).order_by('-id')
        serializer = CustomProcurementEntrySerializer(objs, many=True)

        return Response({
            "data": serializer.data,
            "response": {"n": 1, "msg": "Procurement list", "status": "success"}
        })


class procurement_list_pagination_api(GenericAPIView):
    pagination_class = CustomPagination

    def post(self, request):
        objs = ProcurementEntry.objects.filter(isActive=True).order_by('-id')

        search = request.data.get('search')
        if search:
            objs = objs.filter(
                Q(supplier_id__icontains=search) |
                Q(item_id__icontains=search)
            )

        page = self.paginate_queryset(objs)
        serializer = CustomProcurementEntrySerializer(page, many=True)

        return self.get_paginated_response(serializer.data)

class procurementpayment(GenericAPIView):
    def post(self, request):
        entry_id = request.data.get('entry_id')
        amount = float(request.data.get('amount'))

        entry = ProcurementEntry.objects.filter(id=entry_id).first()

        entry.paid_amount += amount
        entry.credit_amount = entry.total - entry.paid_amount
        entry.save()

        return Response({
            "data": {},
            "response": {"n": 1, "msg": "Payment updated", "status": "success"}
        })



class requirement_by_order(GenericAPIView):

    def post(self, request):

        order_id = request.data.get("order_id")

        if not order_id:
            return Response({
                "data": {
                    "products": [],
                    "procurement_items": []
                },
                "response": {
                    "n": 0,
                    "msg": "Please enter order id"
                }
            })

        order_items = OrderItem.objects.filter(
            order=order_id
        )

        if not order_items.exists():
            return Response({
                "data": {
                    "products": [],
                    "procurement_items": []
                },
                "response": {
                    "n": 0,
                    "msg": "Order items not found"
                }
            })

        product_data = []
        procurement_summary = {}

        product_variants = ProductVariant.objects.filter(
            isActive=True
        )

        products = Product.objects.filter(
            isActive=True
        )

        raw_products = RawProductMaster.objects.filter(
            isActive=True
        )
        units = UnitMaster.objects.filter(
            isActive=True
        )

        for item in order_items:
            ordered_qty = float(item.quantity or 0)

            stock = (
                Inventory.objects.filter(
                    stock_id=item.product_variant
                ).aggregate(
                    total=Sum("quantity")
                )["total"] or 0
            )

            required_product_qty = max(
                0,
                ordered_qty - stock
            )

            variant = product_variants.filter(
                id=item.product_variant
            ).first()
            print("variant",variant)
            product_name = ""
            product_id = ""
            pack_size = 1
            product_unit = ""
            product_unit_name = ""

            if variant:

                pack_size = float(
                    variant.pack_size or 1
                )

                product_id = variant.product

                product_obj = products.filter(
                    id=variant.product
                ).first()

                if product_obj:
                    product_name = product_obj.name
                    product_unit = product_obj.unit
                    
                    if product_obj.unit is not None and product_obj.unit !='':
                        unit_obj=UnitMaster.objects.filter(id=product_obj.unit,isActive=True).first()
                        if unit_obj is not None:
                            product_unit_name = unit_obj.short_name

            if required_product_qty <= 0:

                product_data.append({
                    "product_name": product_name,
                    "product_variant": item.product_variant,
                    "product_id": product_id,
                    "ordered_qty": ordered_qty,
                    "available_stock": stock,
                    "required_qty": 0,
                    "mapping_exist": False,
                    "product_unit": product_unit,
                    "product_unit_name": product_unit_name,
                    
                    "pack_size": pack_size,
                })

                continue

            active_recipe = RecipeMaster.objects.filter(
                product=str(product_id),
                status="active",
                isActive=True
            ).first()

            mappings = RecipeRawmaterial.objects.none()
            mapping_exist = False

            if active_recipe:

                mappings = RecipeRawmaterial.objects.filter(
                    recipe_id=str(active_recipe.id),
                    isActive=True
                )

                mapping_exist = mappings.exists()
            else:
                print("No Active  recipe")
                
                
            product_data.append({
                "product_name": product_name,
                "product_variant": item.product_variant,
                "product_id": product_id,
                "ordered_qty": ordered_qty,
                "available_stock": stock,
                "required_qty": required_product_qty,
                "mapping_exist": mapping_exist,
                "product_unit": product_unit,
                "product_unit_name": product_unit_name,
                "pack_size": pack_size,
            })

            if not active_recipe:
                continue

            output_qty = float(
                active_recipe.standard_output_qty or 1
            )

            production_qty = (
                required_product_qty * pack_size
            )

            for raw in mappings:
                print("raw",raw)
                recipe_qty = float(
                    raw.quantity or 0
                )
                # print("recipe_qty",recipe_qty)
                # required_raw_qty = (
                #     recipe_qty / output_qty
                # ) * production_qty
                # print("required_raw_qty",required_raw_qty)
                # wastage = float(
                #     raw.wastage_percent or 0
                # )

                # required_raw_qty += (
                #     required_raw_qty * wastage / 100
                # )
                
                
                required_raw_qty = recipe_qty

                item_id = str(raw.raw_product_id)

                if item_id not in procurement_summary:
                    procurement_summary[item_id] = 0

                procurement_summary[item_id] += required_raw_qty

        procurement_data = []

        for item_id, qty in procurement_summary.items():

            raw_item = raw_products.filter(
                id=item_id
            ).first()
            unit_id=raw_item.unit if raw_item else ""
            unit_name=''
            if unit_id is not None:
                unit_nobj=units.filter(id=unit_id).first()
                if unit_nobj is not None:
                    unit_name=unit_nobj.short_name
                
            procurement_data.append({

                "procurement_item": item_id,

                "procurement_item_name":
                    raw_item.name if raw_item else "",

                "unit":
                    raw_item.unit if raw_item else "",
                    
                "unit_name":unit_name,

                "required_qty":
                    round(qty, 2)
            })

        return Response({

            "data": {
                "products": product_data,
                "procurement_items": procurement_data
            },

            "response": {
                "n": 1,
                "msg": "Requirement calculated"
            }
        })
    


class addrawproductmaster(GenericAPIView):

    def post(self, request):

        data = {
            'item_code': str(request.data.get('item_code')).upper(),
            'name': str(request.data.get('name')).lower(),
            'category': request.data.get('category'),
            'unit': request.data.get('unit'),
            'is_milk': request.data.get('is_milk') == 'true'
        }

        if not data['item_code'] or not data['name']:
            return Response({
                "response": {"n": 0, "msg": "Item code & name required", "status": "error"}
            })

        if RawProductMaster.objects.filter(item_code=data['item_code'], isActive=True).exists():
            return Response({
                "response": {"n": 0, "msg": "Item already exists", "status": "error"}
            })

        serializer = RawProductMasterSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response({
                "data": serializer.data,
                "response": {"n": 1, "msg": "Item added", "status": "success"}
            })

        return Response({"response": {"n": 0, "msg": "Error", "status": "error"}})

class rawproductmaster_list_pagination_api(GenericAPIView):
    pagination_class = CustomPagination

    def post(self, request):

        objs = RawProductMaster.objects.filter(isActive=True).order_by('-id')

        search = request.data.get('search')

        if search:
            objs = objs.filter(
                Q(item_code__icontains=search) |
                Q(name__icontains=search) |
                Q(category__icontains=search)
            )

        page = self.paginate_queryset(objs)
        serializer = CustomRawProductMasterSerializer(page, many=True)

        return self.get_paginated_response(serializer.data)

class rawproductmasterlist(GenericAPIView):

    def post(self, request):

        objs = RawProductMaster.objects.filter(isActive=True).order_by('-id')

        search = request.data.get('search')

        if search:
            objs = objs.filter(
                Q(item_code__icontains=search) |
                Q(name__icontains=search) |
                Q(category__icontains=search)
            )

        serializer = RawProductMasterSerializer(objs, many=True)

        return Response({
                            "data": serializer.data,
            "response": {"n": 1, "msg": "data found"}
            })



class rawproductmasterupdate(GenericAPIView):

    def post(self, request):

        id = request.data.get('itemid')

        obj = RawProductMaster.objects.filter(id=id, isActive=True).first()

        if not obj:
            return Response({"response": {"n": 0, "msg": "Item not found"}})

        data = {
            'item_code': str(request.data.get('item_code')).upper(),
            'name': str(request.data.get('name')).lower(),
            'category': request.data.get('category'),
            'unit': request.data.get('unit'),
            'is_milk': request.data.get('is_milk') == 'true'
        }

        serializer = RawProductMasterSerializer(obj, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({
                "response": {"n": 1, "msg": "Updated"}
            })

        return Response({"response": {"n": 0, "msg": "Error"}})


class rawproductmasterdelete(GenericAPIView):

    def post(self, request):

        id = request.data.get('itemid')

        obj = RawProductMaster.objects.filter(id=id, isActive=True).first()

        if not obj:
            return Response({"response": {"n": 0, "msg": "Item not found"}})

        obj.isActive = False
        obj.save()

        return Response({"response": {"n": 1, "msg": "Deleted"}})

class rawproductmasterbyid(GenericAPIView):

    def post(self, request):

        id = request.data.get('itemid')

        obj = RawProductMaster.objects.filter(id=id, isActive=True).first()

        if obj:
            serializer = RawProductMasterSerializer(obj)
            return Response({"data": serializer.data, "response": {"n": 1}})

        return Response({"response": {"n": 0, "msg": "Not found"}})




class createrecipe(GenericAPIView):
    @transaction.atomic
    def post(self, request):
        try:
            # -----------------------------
            # Recipe Master Data
            # -----------------------------
            recipe_data = {
                "recipe_code": request.data.get("recipe_code"),
                "recipe_name": request.data.get("recipe_name"),
                "product": request.data.get("product_id"),
                "version": request.data.get("version"),
                "standard_output_qty": request.data.get("standard_output_qty"),
                "output_unit": request.data.get("output_unit"),
                "remarks": request.data.get("remarks"),
            }
            print("request.data",request.data)

            serializer = RecipeMasterSerializer(data=recipe_data)

            if not serializer.is_valid():
                first_key, first_value = next(iter(serializer.errors.items()))
                print("1",f"{first_key} : {first_value[0]}")
                return Response(
                    {
                        "data": serializer.errors,
                        "response": {
                            "n": 0,
                            "msg": f"{first_key} : {first_value[0]}",
                            "status": "error",
                        },
                    },
                    
                )

            recipe = serializer.save()

            # -----------------------------
            # Parse Inputs JSON
            # -----------------------------
            try:
                inputs = json.loads(request.data.get("inputs", "[]"))
            except json.JSONDecodeError:
                transaction.set_rollback(True)
                return Response(
                    {
                        "response": {
                            "n": 0,
                            "msg": "Invalid inputs JSON",
                            "status": "error",
                        }
                    },
                )

            # -----------------------------
            # Save Recipe Inputs
            # -----------------------------
            recipe_inputs = []

            for item in inputs:
                procurement_item_id = item.get("procurement_item_id")
                quantity = item.get("quantity")
                unit = item.get("unit")

                if not procurement_item_id:
                    raise ValueError("Procurement Item is required")

                if not quantity:
                    raise ValueError("Input Quantity is required")

                recipe_inputs.append(
                    RecipeRawmaterial(
                        recipe_id=recipe.id,
                        raw_product_id=procurement_item_id,
                        quantity=float(quantity),
                        unit=unit,
                        wastage_percent=float(
                            item.get("wastage_percent") or 0
                        ),
                    )
                )
            for obj in recipe_inputs:
                print("recipe_id =", obj.recipe_id)
                print("raw_product_id =", obj.raw_product_id)
                print("quantity =", obj.quantity)
                print("unit =", obj.unit, len(str(obj.unit)))
                print("wastage_percent =", obj.wastage_percent)
            RecipeRawmaterial.objects.bulk_create(recipe_inputs)

            # -----------------------------
            # Parse Outputs JSON
            # -----------------------------
            # try:
            #     outputs = json.loads(request.data.get("outputs", "[]"))
            # except json.JSONDecodeError:
            #     transaction.set_rollback(True)
            #     return Response(
            #         {
            #             "response": {
            #                 "n": 0,
            #                 "msg": "Invalid outputs JSON",
            #                 "status": "error",
            #             }
            #         },
            #     )

            # -----------------------------
            # Save Recipe Outputs
            # -----------------------------
            # recipe_outputs = []

            # for item in outputs:

            #     product_variant_id = item.get("product_variant_id")
            #     quantity = item.get("quantity")

            #     if not product_variant_id:
            #         raise ValueError("Output Product is required")

            #     if not quantity:
            #         raise ValueError("Output Quantity is required")

            #     recipe_outputs.append(
            #         RecipeOutput(
            #             recipe=recipe,
            #             product_variant_id=product_variant_id,
            #             quantity=float(quantity),
            #             unit=item.get("unit"),
            #             is_primary_output=item.get(
            #                 "is_primary_output", False
            #             ),
            #         )
            #     )

            # RecipeOutput.objects.bulk_create(recipe_outputs)

            return Response(
                {
                    "recipe_id": recipe.id,
                    "response": {
                        "n": 1,
                        "msg": "Recipe created successfully",
                        "status": "success",
                    },
                },
            )

        except Exception as e:
            transaction.set_rollback(True)
            print("2",str(e))
            return Response(
                {
                    "response": {
                        "n": 0,
                        "msg": str(e),
                        "status": "error",
                    }
                },
            )
            
            
class mappinglist(GenericAPIView):
    def get(self, request):

        objs = RecipeMaster.objects.filter(isActive=True)
        serializer = RecipeMasterSerializer(objs, many=True)

        return Response({
            "data": serializer.data
        })

class mapping_list_pagination_api(GenericAPIView):
    pagination_class = CustomPagination

    def post(self, request):

        objs = RecipeMaster.objects.filter(isActive=True).order_by('-id')

        search = request.data.get("search")

        if search:
            objs = objs.filter(
                Q(procurement_item__icontains=search) |
                Q(product_variant__icontains=search)
            )

        page = self.paginate_queryset(objs)
        serializer = CustomRecipeMasterSerializer(page, many=True)

        return self.get_paginated_response(serializer.data)

class variant_grouped_mapping_list_pagination_api(GenericAPIView):
    pagination_class = CustomPagination

    def post(self, request):

        objs = RecipeMaster.objects.filter(isActive=True).order_by('-id')

        search = request.data.get("search")

        if search:
            objs = objs.filter(
                Q(procurement_item__icontains=search) |
                Q(product__icontains=search)
            )

        # 🔥 SERIALIZE FIRST
        serializer = CustomRecipeMasterSerializer(objs, many=True)
        data = serializer.data

        # ================= GROUPING =================
        grouped = {}

        for obj in data:

            key = obj['product']  # id
            key_name = obj['product_name']  # 🔥 name

            if key not in grouped:
                grouped[key] = {
                    "product": key,
                    "product_name": key_name,
                    "items": []
                }

            grouped[key]["items"].append(obj)

        # dict → list
        grouped_list = list(grouped.values())

        # ================= PAGINATION =================
        page = self.paginate_queryset(grouped_list)

        return self.get_paginated_response(page)
    
class mappingupdate(GenericAPIView):
    def post(self, request):

        id = request.data.get("mapping_id")
        obj = RecipeMaster.objects.filter(id=id).first()

        serializer = RecipeMasterSerializer(obj, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({
                "response": {"n":1, "msg":"Updated"}
            })

        return Response({
            "response": {"n":0, "msg":serializer.errors}
        })


class mappingdelete(GenericAPIView):
    def post(self, request):

        id = request.data.get("mapping_id")

        obj = RecipeMaster.objects.filter(id=id).first()
        obj.isActive = False
        obj.save()

        return Response({
            "response": {"n":1, "msg":"Deleted"}
        })

class get_mapping_by_product(GenericAPIView):

    def post(self, request):
        print("request.data",request.data)
        product = request.data.get("product")

        objs = RecipeMaster.objects.filter(
            product=product,
            isActive=True,status="active"
        ).first()

        if objs:
            serializer = CustomRecipeMasterSerializer(objs)
            raw_products_objs=RecipeRawmaterial.objects.filter(recipe_id=serializer.data['id'],isActive=True)
            raw_products_serializer=CustomRecipeRawmaterialSerializer(raw_products_objs,many=True)
            data=serializer.data
            data['raw_products']=raw_products_serializer.data
            
            return Response({
                "data": data,
                "response": {"n": 1, "msg": "Procurement items mapped to this product", "status": "success"}
            })
        else:
            return Response({
                "data": [],
                "response": {"n": 0, "msg": "Procurement items not mapped to this product", "status": "error"}
            })

class create_procurement(GenericAPIView):

    @transaction.atomic
    def post(self, request):

        try:
            supplier_id = request.data.get("supplier_id")
            products = request.data.get("products", [])
            print("request.data",request.data)
            # quantity = float(request.data.get("quantity") or 0)
            paid_amount = float(request.data.get("paid_amount") or 0)
            order_id = request.data.get("order_id")
            orders_obj=None
            if order_id is not None and order_id !='':
                orders_obj=Order.objects.filter(id=order_id,isActive=True).first()
                if orders_obj is not None:
                    if orders_obj.status =='placed' or orders_obj.status =='pending' :
                        return Response({"response": {"n": 0, "msg": "Order must be confirmed by the admin before procurement can begin."}})
                    elif orders_obj.status =='procurement':
                        return Response({"response": {"n": 0, "msg": "This order has already been moved to procurement."}})
                    elif orders_obj.status =='production-ready':
                        return Response({"response": {"n": 0, "msg": "This order is already ready for production and cannot be moved back to procurement."}})
                    elif orders_obj.status =='production':
                        return Response({"response": {"n": 0, "msg": "This order is already in production and cannot be moved back to procurement."}})
                    elif orders_obj.status =='dispatched-ready':
                        return Response({"response": {"n": 0, "msg": "This order has already ready for dispatched and cannot be moved to procurement."}})
                    elif orders_obj.status =='dispatched':
                        return Response({"response": {"n": 0, "msg": "This order has already been dispatched and cannot be moved to procurement."}})
                    elif orders_obj.status =='delivered':
                        return Response({"response": {"n": 0, "msg": "This order has already been delivered and cannot be moved to procurement."}})
                    elif orders_obj.status =='confirmed':
                        orders_obj.status='procurement'
                else:
                    return Response({"response": {"n": 0, "msg": "order not found"}})
            items = request.data.get("items", [])

          
            if not supplier_id:
                return Response({"response": {"n": 0, "msg": "Please select supplier"}})
            if not products:
                return Response({"response":{"n":0,"msg":"Products required","status":"error"}})

            if not items or len(items) == 0:
                return Response({"response": {"n": 0, "msg": "No items provided"}})

            # ================= CREATE HEADER =================
            entry = ProcurementEntry.objects.create(
                supplier_id=supplier_id,
                order_id=order_id,
                paid_amount=paid_amount
            )
            
            # ================= PRODUCTS =================
            for p in products:
                ProcurementProducts.objects.create(
                    procurement=str(entry.id),
                    product_id=p.get("product_id"),
                    quantity=p.get("quantity"),
                    unit=p.get("unit"),
                    
                )
                
                
            total_amount = 0

            # ================= CREATE ITEMS =================
            for i in items:

                item_id = i.get("item_id")
                qty = float(i.get("quantity") or 0)
                rate = float(i.get("rate") or 0)
                unit = i.get("unit") or ""
                fat = i.get("fat")
                snf = i.get("snf")

                if not item_id or qty <= 0:
                    continue

                item_total = qty * rate

                ProcurementRawmaterial.objects.create(
                    procurement=str(entry.id),
                    raw_material_id=item_id,
                    quantity=qty,
                    unit=unit,
                    fat=fat,
                    snf=snf,
                    rate=rate,
                    total=item_total
                )

                total_amount += item_total

            # ================= UPDATE TOTALS =================
            credit_amount = total_amount - paid_amount

            entry.total_amount = total_amount
            entry.credit_amount = credit_amount
            entry.save()
            if orders_obj is not None:
                orders_obj.save()
            return Response({
                "data": {
                    "procurement_id": entry.id,
                    "total_amount": total_amount,
                    "credit_amount": credit_amount
                },
                "response": {
                    "n": 1,
                    "msg": "Procurement created successfully",
                    "status": "success"
                }
            })

        except Exception as e:
            return Response({
                "response": {
                    "n": 0,
                    "msg": str(e),
                    "status": "error"
                }
            })

class procurement_details(GenericAPIView):

    def post(self, request):

        pid = request.data.get("id")

        if not pid:
            return Response({
                "data": {},
                "response": {"n": 0, "msg": "Procurement ID required", "status": "error"}
            })

        entry = ProcurementEntry.objects.filter(id=pid).first()

        if not entry:
            return Response({
                "data": {},
                "response": {"n": 0, "msg": "Invalid procurement", "status": "error"}
            })

        items = ProcurementRawmaterial.objects.filter(procurement=str(pid))
        items_serializer=CustomProcurementRawmaterialSerializer(items,many=True)

        products = ProcurementProducts.objects.filter(procurement=str(pid))
        products_serializer=CustomProcurementProductsSerializer(products,many=True)
        return Response({
            "data": {
                "entry": {
                    "supplier_id": entry.supplier_id,
                    # "product_id": entry.product_id,
                    # "product_name": entry.product_name,
                    "total": entry.total_amount,
                    "status": entry.status
                },
                "items": items_serializer.data,
                "products":products_serializer.data,

            },
            "response": {"n": 1, "msg": "Details fetched", "status": "success"}
        })
    

def convert_to_base_unit(quantity, unit_id):
    """
    Converts a quantity to its base unit.

    Examples:
        35 LTR -> 35000 ML
        25 KG  -> 25000 GM
        2 MT   -> 2000000 GM
        500 ML -> 500 ML
    """

    unit = UnitMaster.objects.get(id=unit_id)
    qty = Decimal(str(quantity))

    while unit.parent_unit:
        qty *= Decimal(str(unit.conversion_factor))
        unit = unit.parent_unit

    return {
        "quantity": float(qty),   # or return Decimal if your model uses DecimalField
        "unit_id": unit.id
    }
    
    
    
class complete_procurement(GenericAPIView):
    @transaction.atomic
    def post(self, request):

        pid = request.data.get("id")
        outputs = request.data.get("outputs", [])
        
        print("outputs",outputs)

        entry = ProcurementEntry.objects.select_for_update().filter(id=pid).first()

        if not entry:
            return Response({"response":{"n":0,"msg":"Invalid","status":"error"}})

        if entry.status == "completed":
            return Response({"response":{"n":0,"msg":"Already completed","status":"error"}})

        if not outputs:
            return Response({"response":{"n":0,"msg":"No outputs provided","status":"error"}})

        
        
        today_str = datetime.date.today()
        batch = f"BH-RAW-{today_str}-{str(pid).zfill(4)}"
        # ================= SAVE OUTPUT =================
        for o in outputs:
            result = convert_to_base_unit(
                quantity=o.get("quantity"),
                unit_id=o.get("unit")
            )
            # print("result",result,o.get("quantity"))
            # return Response({"response":{"n":0,"msg":"No outputs provided","status":"error"}})
            inventory_qty = result["quantity"]
            inventory_unit = result["unit_id"]

            # Inventory.objects.create(
            #     warehouse="MAIN",
            #     stock_id=o.get("raw_product_id"),
            #     quantity=inventory_qty,
            #     unit=inventory_unit,
            #     inventory_type="raw",
            #     batch=batch
            # )
            
            
            
            if inventory_qty <= 0:
                return Response({"response":{"n":0,"msg":"Invalid quantity","status":"error"}})



            # ================= INVENTORY UPDATE =================
            # create batch no dynamicaly "BH"+Date+"-"+entry.id

            inv = Inventory.objects.filter(
                stock_id=o.get("raw_product_id"),inventory_type='raw',batch=batch
            ).first()

            if inv:
                inv.quantity += inventory_qty
                inv.save()
            else:
                Inventory.objects.create(
                    warehouse="MAIN",
                    stock_id=o.get("raw_product_id"),
                    quantity=inventory_qty,inventory_type='raw',batch=batch,unit=inventory_unit,
                )


        if entry.order_id is not None and entry.order_id !='':
            order_obj=Order.objects.filter(id=entry.order_id).first()
            if order_obj is not None:
                order_obj.status="production-ready"
                order_obj.save()
                
                
        entry.status = "completed"
        entry.save()
        

        return Response({
            "data": {},
            "response": {"n":1,"msg":"Completed & inventory updated","status":"success"}
        })

class delete_procurement(GenericAPIView):

    def post(self, request):

        pid = request.data.get("id")

        if not pid:
            return Response({
                "data": {},
                "response": {"n": 0, "msg": "ID required", "status": "error"}
            })

        entry = ProcurementEntry.objects.filter(id=pid).first()

        if not entry:
            return Response({
                "data": {},
                "response": {"n": 0, "msg": "Invalid procurement", "status": "error"}
            })

        if entry.status == "completed":
            return Response({
                "data": {},
                "response": {"n": 0, "msg": "Cannot delete completed procurement", "status": "error"}
            })

        ProcurementRawmaterial.objects.filter(procurement=str(pid)).update(isActive=False)
        entry.isActive=False
        entry.save()

        return Response({
            "data": {},
            "response": {"n": 1, "msg": "Deleted successfully", "status": "success"}
        })
        
        
        
        
class recipe_list_pagination_api(GenericAPIView):
    pagination_class = CustomPagination

    def post(self, request):

        objs = RecipeMaster.objects.filter(
            isActive=True
        ).order_by('-id')

        search = request.data.get('search')
        status = request.data.get('status')

        if search:
            objs = objs.filter(
                Q(recipe_code__icontains=search) |
                Q(recipe_name__icontains=search) |
                Q(product__icontains=search)
            )

        if status:
            objs = objs.filter(status=status)

        page = self.paginate_queryset(objs)

        serializer = CustomRecipeMasterSerializer(
            page,
            many=True
        )

        return self.get_paginated_response(
            serializer.data
        )
        
class CloneRecipeAPI(GenericAPIView):

    @transaction.atomic
    def post(self, request):

        recipe_id = request.data.get("recipe_id")

        try:

            recipe = RecipeMaster.objects.get(
                id=recipe_id,
                isActive=True
            )

            new_recipe = RecipeMaster.objects.create(
                recipe_code=recipe.recipe_code,
                recipe_name=recipe.recipe_name,
                product=recipe.product,
                version=recipe.version + 1,
                standard_output_qty=recipe.standard_output_qty,
                output_unit=recipe.output_unit,
                remarks=recipe.remarks,
                status='draft'
            )

            raws = RecipeRawmaterial.objects.filter(
                recipe_id=str(recipe.id)
            )

            RecipeRawmaterial.objects.bulk_create([
                RecipeRawmaterial(
                    recipe_id=str(new_recipe.id),
                    raw_product_id=raw.raw_product_id,
                    quantity=raw.quantity,
                    unit=raw.unit,
                    wastage_percent=raw.wastage_percent,
                    remarks=raw.remarks
                )
                for raw in raws
            ])

            return Response({
                "response": {
                    "n": 1,
                    "msg": f"Recipe Version V{new_recipe.version} created",
                    "status": "success"
                }
            })

        except Exception as e:

            return Response({
                "response": {
                    "n": 0,
                    "msg": str(e),
                    "status": "error"
                }
            })
            
            
class ActivateRecipeAPI(GenericAPIView):

    def post(self, request):

        recipe_id = request.data.get("recipe_id")

        try:

            recipe = RecipeMaster.objects.get(
                id=recipe_id,
                isActive=True
            )

            RecipeMaster.objects.filter(
                recipe_code=recipe.recipe_code
            ).update(
                status='inactive'
            )

            recipe.status = 'active'
            recipe.save()

            return Response({
                "response": {
                    "n": 1,
                    "msg": "Recipe activated successfully",
                    "status": "success"
                }
            })

        except Exception as e:

            return Response({
                "response": {
                    "n": 0,
                    "msg": str(e),
                    "status": "error"
                }
            })
            
            
class DeactivateRecipeAPI(GenericAPIView):

    def post(self, request):

        recipe_id = request.data.get("recipe_id")

        try:

            recipe = RecipeMaster.objects.get(
                id=recipe_id,
                isActive=True
            )

            recipe.status = 'inactive'
            recipe.save()

            return Response({
                "response": {
                    "n": 1,
                    "msg": "Recipe deactivated successfully",
                    "status": "success"
                }
            })

        except Exception as e:

            return Response({
                "response": {
                    "n": 0,
                    "msg": str(e),
                    "status": "error"
                }
            })
            
            
            
class DeleteRecipeAPI(GenericAPIView):

    def post(self, request):

        recipe_id = request.data.get("recipe_id")

        try:

            RecipeMaster.objects.filter(
                id=recipe_id
            ).update(
                isActive=False
            )

            RecipeRawmaterial.objects.filter(
                recipe_id=str(recipe_id)
            ).update(
                isActive=False
            )

            return Response({
                "response": {
                    "n": 1,
                    "msg": "Recipe deleted successfully",
                    "status": "success"
                }
            })

        except Exception as e:

            return Response({
                "response": {
                    "n": 0,
                    "msg": str(e),
                    "status": "error"
                }
            })      
            
class recipe_details(GenericAPIView):

    def get(self, request):

        recipe_id = request.GET.get("recipe_id")

        try:

            recipe = RecipeMaster.objects.get(
                id=recipe_id,
                isActive=True
            )

            recipe_data = CustomRecipeMasterSerializer(
                recipe
            ).data

            raw_materials = RecipeRawmaterial.objects.filter(
                recipe_id=str(recipe.id),
                isActive=True
            )

            raw_material_list = []

            for raw in raw_materials:

                raw_product_name = None

                raw_product = RawProductMaster.objects.filter(
                    id=raw.raw_product_id
                ).first()

                if raw_product:
                    raw_product_name = raw_product.name

                unit_name = None

                unit = UnitMaster.objects.filter(
                    id=raw.unit
                ).first()

                if unit:
                    unit_name = unit.short_name
                print("raw.quantity",raw.quantity)
                raw_material_list.append({
                    "id": raw.id,
                    "raw_product_id": raw.raw_product_id,
                    "raw_product_name": raw_product_name,
                    "quantity": raw.quantity,
                    "unit": raw.unit,
                    "unit_name": unit_name,
                    "wastage_percent": raw.wastage_percent,
                    "remarks": raw.remarks
                })

            recipe_data["raw_materials"] = raw_material_list

            return Response({
                "response": {
                    "n": 1,
                    "msg": "Success",
                    "status": "success"
                },
                "data": recipe_data
            })

        except RecipeMaster.DoesNotExist:

            return Response({
                "response": {
                    "n": 0,
                    "msg": "Recipe not found",
                    "status": "error"
                }
            })
            
class UpdateRecipe(GenericAPIView):

    @transaction.atomic
    def post(self, request):
        print("request.data",request.data)
        recipe = RecipeMaster.objects.get(
            id=request.data.get("recipe_id")
        )

        recipe.recipe_name = request.data.get("recipe_name")
        recipe.product = request.data.get("product_id")
        recipe.standard_output_qty = request.data.get("standard_output_qty")
        recipe.output_unit = request.data.get("output_unit")
        recipe.remarks = request.data.get("remarks")
        recipe.save()

        RecipeRawmaterial.objects.filter(
            recipe_id=str(recipe.id)
        ).delete()

        inputs = json.loads(
            request.data.get("inputs", "[]")
        )

        for item in inputs:

            if (
                not item.get("procurement_item_id")
                or not item.get("quantity")
                or not item.get("unit")
            ):
                continue

            RecipeRawmaterial.objects.create(
                recipe_id=str(recipe.id),
                raw_product_id=item["procurement_item_id"],
                quantity=float(item["quantity"]),
                unit=item["unit"],
                wastage_percent=float(
                    item.get("wastage_percent", 0)
                )
            )

        return Response({
            "response":{
                "n":1,
                "msg":"Recipe Updated",
                "status":"success"
            }
        })
            
            
class get_product_recipe_list(GenericAPIView):

    def post(self, request):



        product=request.data.get('product')
        if product is None or product=='':
            return Response({
                "data":[],
                "response":{
                    "n":0,
                    "msg":"Please provide product Id",
                    "status":"error"
                }
            })
        objs = RecipeMaster.objects.filter(
            isActive=True,status='active',product=product
        ).order_by('version')
        
        
        serializer = CustomRecipeMasterSerializer(
            objs,
            many=True
        )

        return Response({
            "data":serializer.data,
            "response":{
                "n":1,
                "msg":"Recipe found successfully",
                "status":"success"
            }
        })
            
            
            
            
            
            
            
            
            
            
            
            
            