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
            product_variant=item_id,
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

        order_id = request.data.get('order_id')
        if order_id is None or order_id =='':
            return Response({
                "data": {
                    "products": [],
                    "procurement_items": []
                },
                "response": {"n": 0, "msg": "Please enter order id"}
            })
        order_items = OrderItem.objects.filter(order=order_id)
        if order_items.count() == 0:
            return Response({
                "data": {
                    "products": [],
                    "procurement_items": []
                },
                "response": {"n": 0, "msg": "Order items not found"}
            })
        
        product_data = []
        procurement_summary = {}

        product_variant_qs = ProductVariant.objects.filter(isActive=True)
        product_qs = Product.objects.filter(isActive=True)
        item_master = ProcurementItemMaster.objects.filter(isActive=True)

        for i in order_items:

            ordered_qty = i.quantity

            # STOCK
            stock = Inventory.objects.filter(
                product_variant=i.product_variant
            ).aggregate(total=Sum('quantity'))['total'] or 0

            required_product_qty = max(0, ordered_qty - stock)

            # PRODUCT NAME
            product_name = ""
            variant_obj = product_variant_qs.filter(id=i.product_variant).first()
            product_id=''
            product_unit=''
            pack_size=0

            if variant_obj:
                product_obj = product_qs.filter(id=variant_obj.product).first()
                if product_obj:
                    product_name = product_obj.name
                    product_id=variant_obj.product
                    pack_size=variant_obj.pack_size
                    product_unit=product_obj.unit




            # SKIP if no need
            if required_product_qty <= 0:
                continue

            # MAPPING
            mappings = ProcurementToProductMapping.objects.filter(
                product=i.product,
                isActive=True
            )
            if mappings.exists():
                mapping_exist=True
            else:
                mapping_exist=False

            # TABLE 1 (PRODUCTS)
            product_data.append({
                "product_name": product_name,
                "product_variant": i.product_variant,
                "product_id": product_id,
                "ordered_qty": ordered_qty,
                "available_stock": stock,
                "required_qty": required_product_qty,
                "mapping_exist":mapping_exist,
                "product_unit":product_unit,
                "pack_size":pack_size,

            })
            for m in mappings:

                item_id = m.procurement_item
                factor = m.conversion_factor

                required_raw = required_product_qty * factor * float(pack_size)

                if item_id not in procurement_summary:
                    procurement_summary[item_id] = 0

                procurement_summary[item_id] += required_raw

        # TABLE 2 (PROCUREMENT ITEMS)
        procurement_data = []
        print("procurement_summary",procurement_summary)
        for item_id, qty in procurement_summary.items():
            item_obj = item_master.filter(id=item_id).first()

            procurement_data.append({
                "procurement_item": item_id,
                "procurement_item_name": item_obj.name if item_obj else "",
                "unit": item_obj.unit if item_obj else "",
                "required_qty": round(qty, 2)
            })

        return Response({
            "data": {
                "products": product_data,
                "procurement_items": procurement_data
            },
            "response": {"n": 1, "msg": "Requirement calculated"}
        })
    


class addprocurementitemmaster(GenericAPIView):

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

        if ProcurementItemMaster.objects.filter(item_code=data['item_code'], isActive=True).exists():
            return Response({
                "response": {"n": 0, "msg": "Item already exists", "status": "error"}
            })

        serializer = ProcurementItemMasterSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response({
                "data": serializer.data,
                "response": {"n": 1, "msg": "Item added", "status": "success"}
            })

        return Response({"response": {"n": 0, "msg": "Error", "status": "error"}})

class procurementitemmaster_list_pagination_api(GenericAPIView):
    pagination_class = CustomPagination

    def post(self, request):

        objs = ProcurementItemMaster.objects.filter(isActive=True).order_by('-id')

        search = request.data.get('search')

        if search:
            objs = objs.filter(
                Q(item_code__icontains=search) |
                Q(name__icontains=search) |
                Q(category__icontains=search)
            )

        page = self.paginate_queryset(objs)
        serializer = ProcurementItemMasterSerializer(page, many=True)

        return self.get_paginated_response(serializer.data)

class procurementitemmasterlist(GenericAPIView):

    def post(self, request):

        objs = ProcurementItemMaster.objects.filter(isActive=True).order_by('-id')

        search = request.data.get('search')

        if search:
            objs = objs.filter(
                Q(item_code__icontains=search) |
                Q(name__icontains=search) |
                Q(category__icontains=search)
            )

        serializer = ProcurementItemMasterSerializer(objs, many=True)

        return Response({
                            "data": serializer.data,
            "response": {"n": 1, "msg": "data found"}
            })



class procurementitemmasterupdate(GenericAPIView):

    def post(self, request):

        id = request.data.get('itemid')

        obj = ProcurementItemMaster.objects.filter(id=id, isActive=True).first()

        if not obj:
            return Response({"response": {"n": 0, "msg": "Item not found"}})

        data = {
            'item_code': str(request.data.get('item_code')).upper(),
            'name': str(request.data.get('name')).lower(),
            'category': request.data.get('category'),
            'unit': request.data.get('unit'),
            'is_milk': request.data.get('is_milk') == 'true'
        }

        serializer = ProcurementItemMasterSerializer(obj, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({
                "response": {"n": 1, "msg": "Updated"}
            })

        return Response({"response": {"n": 0, "msg": "Error"}})


class procurementitemmasterdelete(GenericAPIView):

    def post(self, request):

        id = request.data.get('itemid')

        obj = ProcurementItemMaster.objects.filter(id=id, isActive=True).first()

        if not obj:
            return Response({"response": {"n": 0, "msg": "Item not found"}})

        obj.isActive = False
        obj.save()

        return Response({"response": {"n": 1, "msg": "Deleted"}})

class procurementitemmasterbyid(GenericAPIView):

    def post(self, request):

        id = request.data.get('itemid')

        obj = ProcurementItemMaster.objects.filter(id=id, isActive=True).first()

        if obj:
            serializer = ProcurementItemMasterSerializer(obj)
            return Response({"data": serializer.data, "response": {"n": 1}})

        return Response({"response": {"n": 0, "msg": "Not found"}})




class addmapping(GenericAPIView):
    def post(self, request):

        data = {
            "procurement_item": request.data.get("procurement_item"),
            "product": request.data.get("product"),
            "conversion_factor": request.data.get("conversion_factor"),
            "wastage_percent": request.data.get("wastage_percent") or 0
        }

        serializer = ProcurementToProductMappingSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response({
                "response": {"n":1, "msg":"Mapping added", "status":"success"}
            })

        return Response({
            "response": {"n":0, "msg":serializer.errors, "status":"error"}
        })

class mappinglist(GenericAPIView):
    def get(self, request):

        objs = ProcurementToProductMapping.objects.filter(isActive=True)
        serializer = ProcurementToProductMappingSerializer(objs, many=True)

        return Response({
            "data": serializer.data
        })

class mapping_list_pagination_api(GenericAPIView):
    pagination_class = CustomPagination

    def post(self, request):

        objs = ProcurementToProductMapping.objects.filter(isActive=True).order_by('-id')

        search = request.data.get("search")

        if search:
            objs = objs.filter(
                Q(procurement_item__icontains=search) |
                Q(product_variant__icontains=search)
            )

        page = self.paginate_queryset(objs)
        serializer = CustomProcurementToProductMappingSerializer(page, many=True)

        return self.get_paginated_response(serializer.data)

class variant_grouped_mapping_list_pagination_api(GenericAPIView):
    pagination_class = CustomPagination

    def post(self, request):

        objs = ProcurementToProductMapping.objects.filter(isActive=True).order_by('-id')

        search = request.data.get("search")

        if search:
            objs = objs.filter(
                Q(procurement_item__icontains=search) |
                Q(product__icontains=search)
            )

        # 🔥 SERIALIZE FIRST
        serializer = CustomProcurementToProductMappingSerializer(objs, many=True)
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
        obj = ProcurementToProductMapping.objects.filter(id=id).first()

        serializer = ProcurementToProductMappingSerializer(obj, data=request.data, partial=True)

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

        obj = ProcurementToProductMapping.objects.filter(id=id).first()
        obj.isActive = False
        obj.save()

        return Response({
            "response": {"n":1, "msg":"Deleted"}
        })

class get_mapping_by_product(GenericAPIView):

    def post(self, request):
        print("request.data",request.data)
        product = request.data.get("product")

        objs = ProcurementToProductMapping.objects.filter(
            product=product,
            isActive=True
        )
        print("objs",objs.count())
        if objs.exists():
            serializer = CustomProcurementToProductMappingSerializer(objs, many=True)

            return Response({
                "data": serializer.data,
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

            items = request.data.get("items", [])

            # 🔒 basic validation
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
                    quantity=p.get("quantity")
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

                ProcurementItem.objects.create(
                    procurement=str(entry.id),
                    procurement_item_id=item_id,
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

        items = ProcurementItem.objects.filter(procurement=str(pid))
        items_serializer=CustomProcurementItemSerializer(items,many=True)

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
        batch = f"BH-{today_str}-{str(pid).zfill(4)}"
        # ================= SAVE OUTPUT =================
        for o in outputs:

            ProcurementOutput.objects.create(
                procurement=str(pid),
                product_variant_id=o.get("product_variant_id"),
                quantity=o.get("quantity")
            )
            qty = float(o.get("quantity", 0))
            if qty <= 0:
                return Response({"response":{"n":0,"msg":"Invalid quantity","status":"error"}})



            # ================= INVENTORY UPDATE =================
            # create batch no dynamicaly "BH"+Date+"-"+entry.id

            inv = Inventory.objects.filter(
                product_variant=o.get("product_variant_id"),inventory_type='finished',batch=batch
            ).first()

            if inv:
                inv.quantity += float(o.get("quantity"))
                inv.save()
            else:
                Inventory.objects.create(
                    warehouse="MAIN",
                    product_variant=o.get("product_variant_id"),
                    quantity=o.get("quantity"),inventory_type='finished',batch=batch
                )

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

        ProcurementItem.objects.filter(procurement=str(pid)).update(isActive=False)
        entry.isActive=False
        entry.save()

        return Response({
            "data": {},
            "response": {"n": 1, "msg": "Deleted successfully", "status": "success"}
        })