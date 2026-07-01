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
from Masters.models import *
from Masters.serializers import *
from Orders.models import *
from Orders.serializers import *
from Procurement.models import *
from Procurement.serializers import *
from User.jwt import userJWTAuthentication
from django.template.loader import get_template, render_to_string
from django.core.mail import EmailMessage
from User.common import CustomPagination
from django.db.models import Q
import json, datetime
from Inventory.models import Inventory,Warehouse
from collections import defaultdict
from django.db.models import Sum
from django.db import transaction
from decimal import Decimal
from django.utils import timezone
# Create your views here.
class addprocessingbatch(GenericAPIView):
    def post(self, request):
        batch_number = request.data.get('batch_number')
        input_qty = float(request.data.get('input_quantity') or 0)
        output_qty = float(request.data.get('output_quantity') or 0)

        if ProcessingBatch.objects.filter(batch_number=batch_number).exists():
            return Response({"data": {}, "response": {"n": 0, "msg": "Batch exists", "status": "error"}})

        batch = ProcessingBatch.objects.create(
            batch_number=batch_number,
            input_quantity=input_qty,
            output_quantity=output_qty
        )

        return Response({
            "data": {"batch_id": batch.id},
            "response": {"n": 1, "msg": "Batch created", "status": "success"}
        })
    
class addbatchoutput(GenericAPIView):
    def post(self, request):
        batch_id = request.data.get('batch_id')
        outputs = request.data.get('outputs')  # list

        for item in outputs:
            BatchOutput.objects.create(
                batch=batch_id,
                product_variant=item.get('product_variant'),
                quantity=item.get('quantity')
            )

        return Response({
            "data": {},
            "response": {"n": 1, "msg": "Batch output saved", "status": "success"}
        })

class processingbatchlist(GenericAPIView):
    def get(self, request):
        objs = ProcessingBatch.objects.filter(isActive=True).order_by('-id')
        serializer = ProcessingBatchSerializer(objs, many=True)

        return Response({
            "data": serializer.data,
            "response": {"n": 1, "msg": "Production batches", "status": "success"}
        })
    
class batchdetails(GenericAPIView):
    def post(self, request):
        batch_id = request.data.get('batch_id')

        batch = ProcessingBatch.objects.filter(id=batch_id).first()
        outputs = BatchOutput.objects.filter(batch=str(batch_id))

        return Response({
            "data": {
                "batch": ProcessingBatchSerializer(batch).data,
                "outputs": BatchOutputSerializer(outputs, many=True).data
            },
            "response": {"n": 1, "msg": "Batch details", "status": "success"}
        })





class production_list_pagination_api(GenericAPIView):

    def post(self, request):

        search = request.data.get("search", "")
        status = request.data.get("status", "")
        mode = request.data.get("mode", "")

        qs = ProductionEntry.objects.all().order_by("-id")

        if search:
            qs = qs.filter(
                Q(batch__icontains=search) |
                Q(product_id__icontains=search) |
                Q(order_id__icontains=search)
            )

        if status:
            qs = qs.filter(status=status)

        if mode:
            qs = qs.filter(production_type=mode)

        paginator = CustomPagination()
        page = paginator.paginate_queryset(qs, request)

        data = []
        product_base_query= Product.objects.filter(isActive=True)
        recipe_base_query= RecipeMaster.objects.filter(isActive=True)
        unit_base_query= UnitMaster.objects.filter(isActive=True)
        for obj in page:

            product =product_base_query.filter(id=obj.product_id).first()

            recipe = recipe_base_query.filter(id=obj.recipe_id).first()
            planned_unit_obj = unit_base_query.filter(id=obj.planned_unit).first()
            if planned_unit_obj is not None:
                planned_unit_name=planned_unit_obj.short_name
            else:
                planned_unit_name='NA'
            actual_unit_obj = unit_base_query.filter(id=obj.actual_unit).first()
            if actual_unit_obj is not None:
                actual_unit_name=actual_unit_obj.short_name
            else:
                actual_unit_name='NA'
            data.append({

                "id": obj.id,

                "batch": obj.batch,

                "production_type": obj.production_type,

                "order_id": obj.order_id,

                "product_id": obj.product_id,

                "product_name": product.name if product else "",

                "recipe_id": obj.recipe_id,

                "recipe_name": recipe.recipe_name if recipe else "",

                "planned_quantity": obj.planned_quantity,

                "planned_unit": obj.planned_unit,
                "planned_unit_name": planned_unit_name,

                "actual_quantity": obj.actual_quantity,

                "actual_unit": obj.actual_unit,
                "actual_unit_name": actual_unit_name,

                "status": obj.status,

                "created_at": obj.createdAt.strftime("%d-%m-%Y %I:%M %p"),

            })

        return paginator.get_paginated_response(data)






class generate_recommendation(GenericAPIView):

    def post(self, request):

        recipe_id = request.data.get("recipe_id")
        production_qty = float(request.data.get("quantity", 0))

        if production_qty <= 0:
            return Response({
                "response": {
                    "n": 0,
                    "msg": "Invalid production quantity",
                    "status": "error"
                }
            })

        recipe = RecipeMaster.objects.filter(
            id=recipe_id,
            status="active"
        ).first()

        if not recipe:
            return Response({
                "response": {
                    "n": 0,
                    "msg": "Recipe not found",
                    "status": "error"
                }
            })
        recipe_serializer=CustomRecipeMasterSerializer(recipe)

        recipe_items = RecipeRawmaterial.objects.filter(
            recipe_id=recipe.id
        )
        multiplier = production_qty / recipe.standard_output_qty

        items = []

        estimated_cost = 0

        shortage = False
        for item in recipe_items:

            required_qty = item.quantity * multiplier

            inventory = Inventory.objects.filter(
                stock_id=item.raw_product_id,
                inventory_type="raw"
            ).aggregate(total=Sum("quantity"))

            available_qty = inventory["total"] or 0
            
            available_qty_display = convert_from_base_unit(
                available_qty,
                item.unit
            )
            print("available_qty",available_qty)
            print("available_qty_display",available_qty_display)

            
            raw = RawProductMaster.objects.filter(
                id=item.raw_product_id
            ).first()

            # Latest procurement rate
            latest = ProcurementRawmaterial.objects.filter(
                raw_material_id=item.raw_product_id
            ).order_by("-id").first()

            rate = latest.rate if latest else 0

            estimated_cost += required_qty * rate

            available = available_qty_display >= required_qty
            if not available:
                shortage = True

            unit = UnitMaster.objects.filter(
                id=item.unit
            ).first()

            items.append({

                "raw_product_id": item.raw_product_id,

                "name": raw.name if raw else "",

                "required_qty": round(required_qty, 2),
                "required_qty_units": item.unit,

                "available_qty": round(available_qty_display, 2),

                "unit": item.unit,

                "unit_name": unit.short_name if unit else "",

                "rate": rate,

                "available": available

            })

        batch = f"PB-{datetime.date.today()}-{str(recipe.id).zfill(4)}"

        return Response({

            "data": {

                "recipe_id": recipe.id,
                "recipe_name": recipe.recipe_name,

                "recipe_version": recipe.version,

                "product_id": recipe.product,

                "product_name": Product.objects.filter(
                    id=recipe.product
                ).first().name,

                "output_qty": production_qty,

                "output_unit": recipe.output_unit,
                "output_unit_name": recipe_serializer.data['output_unit_name'],

                "expected_yield": 100,

                "estimated_cost": round(estimated_cost, 2),

                "batch": batch,

                "status": "Ready"
                if not shortage
                else "Shortage",

                "items": items

            },

            "response": {

                "n": 1,

                "msg": "Recommendation generated",

                "status": "success"

            }

        })



def convert_from_base_unit(quantity, target_unit_id):
    """
    Converts a base unit quantity (GM/ML) into the target unit.

    Examples:
        35000 ML -> 35 LTR
        25000 GM -> 25 KG
        500 GM -> 500 GM
    """

    unit = UnitMaster.objects.filter(id=target_unit_id).first()

    if unit is None:
        return quantity

    qty = float(quantity)

    # Target unit is already base
    if unit.parent_unit is None:
        return qty

    return qty / float(unit.conversion_factor)

def convert_to_base_unit(quantity, unit_id):
    """
    Convert any unit to its base unit.

    Examples:
        35 LTR  -> 35000 ML
        25 KG   -> 25000 GM
        2 MT    -> 2000000 GM
        500 ML  -> 500 ML
        750 GM  -> 750 GM

    Returns:
    {
        "quantity": converted_quantity,
        "unit_id": base_unit_id
    }
    """

    unit = UnitMaster.objects.get(id=unit_id)

    qty = Decimal(str(quantity))

    while unit.parent_unit:

        qty *= Decimal(str(unit.conversion_factor))

        unit = unit.parent_unit

    return {
        "quantity": float(qty),
        "unit_id": unit.id
    }
    
    
class create_production(GenericAPIView):

    @transaction.atomic
    def post(self, request):

        try:

            data = json.loads(request.body)

            production_type = data.get("production_type", "manual")
            order_id = data.get("order_id")
            recipe_id = data.get("recipe_id")
            product_id = data.get("product_id")
            quantity = float(data.get("quantity", 0))
            warehouse = data.get("warehouse")
            items = data.get("items", [])

            if quantity <= 0:
                return Response({
                    "response": {
                        "n": 0,
                        "msg": "Invalid production quantity",
                        "status": "error"
                    }
                })

            recipe = RecipeMaster.objects.filter(
                id=recipe_id,
                status="active"
            ).first()

            if recipe is None:
                return Response({
                    "response": {
                        "n": 0,
                        "msg": "Recipe not found",
                        "status": "error"
                    }
                })

            # ------------------------
            # Generate Batch Number
            # ------------------------

            batch = "PB-" + str(ProductionEntry.objects.count() + 1).zfill(5)

            production = ProductionEntry.objects.create(

                production_type=production_type,

                order_id=order_id,

                recipe_id=recipe_id,

                product_id=product_id,

                planned_quantity=quantity,

                planned_unit=recipe.output_unit,

                actual_quantity=0,

                actual_unit=recipe.output_unit,

                warehouse=warehouse,

                batch=batch,

                status="processing"

            )

            # ------------------------
            # Save Planned Consumption
            # ------------------------

            for item in items:

                ProductionInput.objects.create(

                    production=str(production.id),

                    raw_product_id=item["raw_product_id"],

                    quantity=item["quantity"],

                    unit=item["unit"],

                    wastage=0

                )

            # ------------------------
            # Expected Output
            # ------------------------

            ProductionOutput.objects.create(

                production=str(production.id),

                product_id=product_id,

                quantity=quantity,

                unit=recipe.output_unit,

                inventory_batch=batch,

                is_primary=True

            )

            return Response({

                "data": {

                    "production_id": production.id,

                    "batch": batch

                },

                "response": {

                    "n": 1,

                    "msg": "Production batch created successfully.",

                    "status": "success"

                }

            })

        except Exception as e:

            transaction.set_rollback(True)

            return Response({

                "response": {

                    "n": 0,

                    "msg": str(e),

                    "status": "error"

                }

            })

class production_details(GenericAPIView):

    def post(self, request):

        production_id = request.data.get("id")

        production = ProductionEntry.objects.filter(
            id=production_id
        ).first()

        if production is None:
            return Response({
                "response": {
                    "n": 0,
                    "msg": "Invalid Production",
                    "status": "error"
                }
            })

        product = Product.objects.filter(
            id=production.product_id
        ).first()

        recipe = RecipeMaster.objects.filter(
            id=production.recipe_id
        ).first()

        # -----------------------------
        # Raw Materials
        # -----------------------------

        inputs = []

        production_inputs = ProductionInput.objects.filter(
            production=str(production.id)
        )

        for item in production_inputs:

            raw = RawProductMaster.objects.filter(
                id=item.raw_product_id
            ).first()

            unit = UnitMaster.objects.filter(
                id=item.unit
            ).first()



            inputs.append({

                "raw_product_id": item.raw_product_id,

                "name": raw.name if raw else "",

                "required_qty": item.quantity,

                "consumed_qty": item.quantity,

                "unit_name": unit.short_name if unit else "",

                "inventory_batch": item.inventory_batch if hasattr(item, "inventory_batch") else ""

            })

        # -----------------------------
        # Finished Output
        # -----------------------------

        outputs = []

        production_outputs = ProductionOutput.objects.filter(
            production=str(production.id)
        )

        for item in production_outputs:

            product_obj = Product.objects.filter(
                id=item.product_id
            ).first()

            unit = UnitMaster.objects.filter(
                id=item.unit
            ).first()

            outputs.append({

                "product_name": product_obj.name if product_obj else "",

                "expected_qty": item.quantity,

                "actual_qty": production.actual_quantity,

                "unit_name": unit.short_name if unit else "",

                "batch": item.inventory_batch

            })

        # -----------------------------
        # Inventory Movement
        # -----------------------------

        movements = []

        inventory = Inventory.objects.filter(
            batch=production.batch
        )

        for inv in inventory:

            if inv.inventory_type == "raw":
                transaction = "Consumed"
            else:
                transaction = "Produced"

            unit = UnitMaster.objects.filter(
                id=inv.unit
            ).first()

            if inv.inventory_type == "raw":

                raw = RawProductMaster.objects.filter(
                    id=inv.stock_id
                ).first()

                stock_name = raw.name if raw else ""

            else:

                prod = Product.objects.filter(
                    id=inv.stock_id
                ).first()

                stock_name = prod.name if prod else ""

            movements.append({

                "stock_name": stock_name,

                "transaction": transaction,

                "quantity": inv.quantity,

                "unit_name": unit.short_name if unit else "",

                "reference": inv.batch

            })

        # -----------------------------
        # Yield
        # -----------------------------

        if production.actual_quantity > 0:

            yield_percent = round(

                (production.actual_quantity /
                 production.planned_quantity) * 100,

                2

            )

        else:

            yield_percent = 0
        planned_unit_obj = UnitMaster.objects.filter(id=recipe.output_unit).first()
        if planned_unit_obj is not None:
            planned_unit_name=planned_unit_obj.short_name
        else:
            planned_unit_name='NA'
        actual_unit_name=planned_unit_name
        warehouse_obj=Warehouse.objects.filter(id=production.warehouse).first()
        if warehouse_obj is not None:
            warehouse_name=warehouse_obj.name
        else:
            warehouse_name='NA'
            
            
        return Response({

            "data": {

                "id": production.id,

                "batch": production.batch,

                "product_name": product.name if product else "",

                "recipe_name": recipe.recipe_name if recipe else "",

                "order_id": production.order_id,

                "production_type": production.production_type,

                "status": production.status,

                "planned_quantity": production.planned_quantity,

                "planned_unit": recipe.output_unit if recipe else "",
                "planned_unit_name": planned_unit_name,

                "actual_quantity": production.actual_quantity,

                "actual_unit": recipe.output_unit if recipe else "",
                "actual_unit_name": actual_unit_name,

                "yield_percent": yield_percent,

                "total_cost": 0,

                "created_at": production.createdAt.strftime("%d-%m-%Y %I:%M %p"),

                "inputs": inputs,

                "outputs": outputs,
                
                "warehouse": warehouse_name,

                "movements": movements

            },

            "response": {

                "n": 1,

                "msg": "Success",

                "status": "success"

            }

        })

class complete_production(GenericAPIView):

    @transaction.atomic
    def post(self, request):

        production_id = request.data.get("production_id")
        actual_quantity = float(request.data.get("actual_quantity", 0))
        remarks = request.data.get("remarks", "")

        production = ProductionEntry.objects.select_for_update().filter(
            id=production_id
        ).first()

        if production is None:
            return Response({
                "response": {
                    "n": 0,
                    "msg": "Invalid Production",
                    "status": "error"
                }
            })

        if production.status == "completed":
            return Response({
                "response": {
                    "n": 0,
                    "msg": "Production already completed",
                    "status": "error"
                }
            })

        if actual_quantity <= 0:
            return Response({
                "response": {
                    "n": 0,
                    "msg": "Invalid actual quantity",
                    "status": "error"
                }
            })

        ######################################################
        # Consume Raw Inventory (FIFO)
        ######################################################

        inputs = ProductionInput.objects.filter(
            production=str(production.id)
        )

        for item in inputs:

            balance = convert_to_base_unit(
                item.quantity,
                item.unit
            )["quantity"]
            inventories = Inventory.objects.select_for_update().filter(
                stock_id=item.raw_product_id,
                inventory_type="raw",
                quantity__gt=0
            ).order_by("createdAt")

            available = sum(i.quantity for i in inventories)

            if available < balance:

                return Response({
                    "response": {
                        "n": 0,
                        "msg": f"Insufficient inventory for Raw Product {item.raw_product_id}",
                        "status": "error"
                    }
                })

            for inv in inventories:

                if balance <= 0:
                    break

                if inv.quantity >= balance:

                    inv.quantity -= balance
                    inv.save()

                    balance = 0

                else:

                    balance -= inv.quantity

                    inv.quantity = 0
                    inv.save()

        ######################################################
        # Add Finished Inventory
        ######################################################

        output = ProductionOutput.objects.filter(
            production=str(production.id),
            is_primary=True
        ).first()

        if output:
            result=convert_to_base_unit(actual_quantity,output.unit)
            inv = Inventory.objects.filter(
                stock_id=output.product_id,
                inventory_type="finished",
                batch=output.inventory_batch
            ).first()

            if inv:

                inv.quantity += result['quantity']
                inv.save()

            else:

                Inventory.objects.create(

                    warehouse=0,

                    stock_id=output.product_id,

                    quantity=result['quantity'],

                    unit=result['unit_id'],

                    batch=output.inventory_batch,

                    inventory_type="finished"

                )

            output.quantity = actual_quantity
            output.save()

        ######################################################
        # Update Production
        ######################################################

        production.actual_quantity = actual_quantity
        production.remarks = remarks
        production.status = "completed"
        production.updatedAt = timezone.now()
        if production.order_id is not None and production.order_id !='':
            order_obj=Order.objects.filter(id=production.order_id).first()
            if order_obj is not None:
                order_obj.status='dispatch-ready'
                order_obj.save()

        production.save()
        return Response({

            "data": {

                "production_id": production.id

            },

            "response": {

                "n": 1,

                "msg": "Production completed successfully.",

                "status": "success"

            }

        })


class production_dashboard_api(GenericAPIView):

    def post(self, request):

        today = timezone.now().date()

        production_ready = ProductionEntry.objects.filter(
            status="processing"
        ).count()

        in_production = ProductionEntry.objects.filter(
            status="started"
        ).count()

        completed_today = ProductionEntry.objects.filter(
            status="completed",
            updatedAt__date=today
        ).count()

        shortage = 0

        productions = ProductionEntry.objects.filter(
            status__in=["processing", "started"]
        )

        for production in productions:

            inputs = ProductionInput.objects.filter(
                production=str(production.id)
            )

            is_short = False

            for item in inputs:

                inventory = Inventory.objects.filter(
                    stock_id=item.raw_product_id,
                    inventory_type="raw"
                ).aggregate(total=Sum("quantity"))

                available = inventory["total"] or 0

                required = item.quantity

                if available < required:
                    is_short = True
                    break

            if is_short:
                shortage += 1

        return Response({

            "data":{

                "production_ready":production_ready,

                "in_production":in_production,

                "completed_today":completed_today,

                "raw_material_shortage":shortage

            },

            "response":{

                "n":1,

                "msg":"Success",

                "status":"success"

            }

        })

class delete_production(GenericAPIView):

    @transaction.atomic
    def post(self, request):

        production_id = request.data.get("id")

        production = ProductionEntry.objects.filter(
            id=production_id
        ).first()

        if production is None:
            return Response({
                "response": {
                    "n": 0,
                    "msg": "Invalid Production",
                    "status": "error"
                }
            })

        if production.status == "completed":
            return Response({
                "response": {
                    "n": 0,
                    "msg": "Completed production cannot be deleted.",
                    "status": "error"
                }
            })

        ProductionInput.objects.filter(
            production=str(production.id)
        ).delete()

        ProductionOutput.objects.filter(
            production=str(production.id)
        ).delete()

        production.delete()

        return Response({

            "response": {

                "n": 1,

                "msg": "Production deleted successfully.",

                "status": "success"

            }

        })

class order_production_recommendation(GenericAPIView):

    def post(self, request):

        order_id = request.data.get("order_id")

        order = Order.objects.filter(id=order_id).first()

        if order is None:

            return Response({
                "response":{
                    "n":0,
                    "msg":"Invalid Order",
                    "status":"error"
                }
            })
        order_serializer=CustomOrderSerializer(order)
        order_items = OrderItem.objects.filter(
            order=order.id
        )

        if not order_items.exists():

            return Response({
                "response":{
                    "n":0,
                    "msg":"No Order Items",
                    "status":"error"
                }
            })

        ####################################################
        # GROUP BY PARENT PRODUCT
        ####################################################

        grouped_products = defaultdict(float)

        order_item_data = []

        for item in order_items:

            variant = ProductVariant.objects.filter(
                id=item.product_variant
            ).first()
            variant_serializer=CustomProductVariantSerializer(variant)
            if variant is None:
                continue

            product = Product.objects.filter(
                id=variant.product
            ).first()

            if product is None:
                continue

            ####################################################
            # Convert Variant Qty to Parent Product Qty
            ####################################################

            # Example:
            # 300 gm x 10 = 3000 gm

            required_qty = float(item.quantity) * float(variant.pack_size)

            result = convert_to_base_unit(
                required_qty,
                product.unit
            )

            grouped_products[product.id] += result["quantity"]

            order_item_data.append({

                "variant_name":product.name + " " + str(variant.pack_size),

                "quantity":item.quantity,

                "unit":variant.pack_type,

            })

        ####################################################
        # RECOMMENDATIONS
        ####################################################

        recommendations = []

        for product_id, base_qty in grouped_products.items():

            product = Product.objects.get(id=product_id)


            recipe = RecipeMaster.objects.filter(

                product=product_id,

                status="active"

            ).order_by("-version").first()
            recipe_serializer=CustomRecipeMasterSerializer(recipe)
            if recipe is None:
                continue
            
            display_qty=convert_from_base_unit(base_qty,recipe.output_unit)

            multiplier = display_qty / recipe.standard_output_qty

            items = []

            ready = True

            total_cost = 0

            recipe_items = RecipeRawmaterial.objects.filter(
                recipe_id=recipe.id
            )

            for raw in recipe_items:
                print("raw", raw.quantity)
                required_qty = raw.quantity * multiplier
                print("required_qty", required_qty)

                inventory = Inventory.objects.filter(

                    stock_id=raw.raw_product_id,

                    inventory_type="raw"

                ).aggregate(total=Sum("quantity"))

                available = inventory["total"] or 0

                available_display = convert_from_base_unit(

                    available,

                    raw.unit

                )

                raw_product = RawProductMaster.objects.filter(
                    id=raw.raw_product_id
                ).first()

                if available_display < required_qty:

                    ready = False

                items.append({

                    "raw_product_id":raw.raw_product_id,

                    "name":raw_product.name if raw_product else "",

                    "required_qty":round(required_qty,2),

                    "available_qty":round(available_display,2),

                    "unit":UnitMaster.objects.get(id=raw.unit).short_name,

                    "available":available_display >= required_qty

                })

            recommendations.append({

                "product_id":product.id,

                "product_name":product.name,

                "recipe_id":recipe.id,

                "recipe_name":recipe.recipe_name,

                "recipe_version":recipe.version,

                "quantity":round(display_qty,2),

                "unit":recipe.output_unit,
                
                "unit_name":recipe_serializer.data['output_unit_name'],

                "ready":ready,

                "items":items

            })

        ####################################################

        return Response({

            "data":{

                "customer":order_serializer.data['customer_name'],

                "order_date":order.createdAt.strftime("%d-%m-%Y"),

                "delivery_date":order.due_date.strftime("%d-%m-%Y"),

                "status":order.status,

                "order_items":order_item_data,

                "recommendations":recommendations

            },

            "response":{

                "n":1,

                "msg":"Success",

                "status":"success"

            }

        })

class create_order_production(GenericAPIView):

    @transaction.atomic
    def post(self, request):

        try:

            data = json.loads(request.body)
            order_id = data.get("order_id")
            productions = data.get("productions", [])

            if not productions:
                return Response({
                    "response": {
                        "n": 0,
                        "msg": "No production selected.",
                        "status": "error"
                    }
                })
            order_obj=Order.objects.filter(id=order_id).first()
            if order_obj is None:
                return Response({
                    "response": {
                        "n": 0,
                        "msg": "No order found.",
                        "status": "error"
                    }
                })
            created = []

            for production_data in productions:

                product_id = production_data["product_id"]
                recipe_id = production_data["recipe_id"]
                quantity = float(production_data["quantity"])

                recipe = RecipeMaster.objects.filter(
                    id=recipe_id,
                    status="active"
                ).first()

                if recipe is None:
                    continue

                production = ProductionEntry.objects.create(

                    production_type="order",

                    order_id=order_id,

                    recipe_id=recipe.id,

                    product_id=product_id,

                    planned_quantity=quantity,

                    planned_unit=recipe.output_unit,

                    actual_quantity=0,

                    actual_unit=recipe.output_unit,

                    batch="",

                    status="processing"

                )

                batch = "PB-" + str(production.id).zfill(6)

                production.batch = batch
                production.save()

                multiplier = quantity / recipe.standard_output_qty

                recipe_items = RecipeRawmaterial.objects.filter(
                    recipe_id=recipe.id
                )

                for raw in recipe_items:

                    required_qty = raw.quantity * multiplier

                    # result = convert_to_base_unit(
                    #     required_qty,
                    #     raw.unit
                    # )

                    ProductionInput.objects.create(
                        production=str(production.id),
                        raw_product_id=raw.raw_product_id,
                        quantity=required_qty,
                        unit=raw.unit,
                        wastage=raw.wastage_percent
                    )

                ProductionOutput.objects.create(

                    production=str(production.id),

                    product_id=product_id,

                    quantity=quantity,

                    unit=recipe.output_unit,

                    inventory_batch=batch,

                    is_primary=True

                )

                created.append({

                    "production_id": production.id,

                    "batch": batch,

                    "product_id": product_id

                })
                order_obj.status='production'
                order_obj.save()
            return Response({

                "data": {

                    "created": created

                },

                "response": {

                    "n": 1,

                    "msg": str(len(created)) + " Production Batch(es) Created Successfully.",

                    "status": "success"

                }

            })

        except Exception as e:

            transaction.set_rollback(True)

            return Response({

                "response": {

                    "n": 0,

                    "msg": str(e),

                    "status": "error"

                }

            })















