from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from django.db.models import Q
import json, datetime
from Inventory.models import *
from Inventory.serializers import *
from .models import Order, OrderItem, Payment, CustomerPricing
from Customers.models import Customer
from Masters.models import ProductVariant
from .serializers import *
from User.common import CustomPagination
from django.db import transaction
from User.jwt import userJWTAuthentication
from rest_framework import permissions
from Production.views import convert_to_base_unit
from django.db.models import Sum
# 🔥 SAFE FLOAT
def to_float(val, default=0):
    try:
        if val in ["", None]:
            return default
        return float(val)
    except:
        return default


# =====================================================
# 🟢 CREATE ORDER (CART BASED)
# =====================================================
class createorder(GenericAPIView):

    def post(self, request):

        customer_id = request.data.get('customer_id')
        payment_mode = request.data.get('payment_mode')
        paid_amount = to_float(request.data.get('paid_amount'))

        items = request.data.get('items')

        # 🔥 FIX JSON
        if isinstance(items, str):
            items = json.loads(items)

        if not customer_id or not items:
            return Response({
                "data": {},
                "response": {"n": 0, "msg": "Customer & items required", "status": "error"}
            })

        customer = Customer.objects.filter(id=customer_id, isActive=True).first()
        if not customer:
            return Response({
                "data": {},
                "response": {"n": 0, "msg": "Invalid customer", "status": "error"}
            })

        total_amount = 0
        taxable_amount = 0
        gst_amount = 0
        order_items = []

        # 🔥 PRICE CALCULATION
        for item in items:

            variant_id = item.get('product_variant')
            qty = int(item.get('quantity'))
            price = int(item.get('price'))
            variant = ProductVariant.objects.filter(id=variant_id).first()
            gst_percentage=variant.gst_rate
            price_with_gst=price
            
            price_without_gst = round(
                    price_with_gst / (1 + (gst_percentage / 100)),
                    2
                )
            product_gst_amount = round(
                price_with_gst - price_without_gst,
                2
            )
            
            total = round(price_with_gst * qty, 2)
            taxable_amount += round(price_without_gst * qty, 2)
            gst_amount += round(product_gst_amount * qty, 2)
            total_amount += total

            order_items.append({
                "variant": variant_id,
                "qty": qty,
                "price": price,
                "product":variant.product,
                "gst_percentage":gst_percentage,
                "price_without_gst":price_without_gst,
                "total":total,
                "gst_amount":gst_amount,
                
                
            })

        credit_amount = total_amount - paid_amount

        # 🔥 DUE DATE
        due_date = None
        if credit_amount > 0:
            due_date = datetime.date.today() + datetime.timedelta(days=customer.default_credit_days)

        # 🔥 CREATE ORDER
        order = Order.objects.create(
            customer_id=customer_id,
            payment_mode=payment_mode,
            total_amount=total_amount,
            taxable_amount=taxable_amount,
            gst_amount=gst_amount,
            paid_amount=paid_amount,
            credit_amount=credit_amount,
            due_date=due_date,
            status='placed'
        )

        # 🔥 CREATE ITEMS
        for i in order_items:
            OrderItem.objects.create(
                order=str(order.id),
                product_variant=i['variant'],
                product=i['product'],
                quantity=i['qty'],
                price=i['price'],
                gst_percentage=i['gst_percentage'],
                price_without_gst=i['price_without_gst'],
                total=i['total'],
                gst_amount=i['gst_amount'],
                
            )

        # 🔥 UPDATE CUSTOMER BALANCE
        customer.outstanding_balance += credit_amount
        customer.save()

        return Response({
            "data": {"order_id": order.id},
            "response": {"n": 1, "msg": "Order created", "status": "success"}
        })


# =====================================================
# 🟢 ORDER LIST (PAGINATION)
# =====================================================
class order_list_pagination_api(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = CustomPagination

    def post(self, request):

        search = request.data.get('search')

        orders = Order.objects.filter(isActive=True).order_by('-id')
        print("orders",orders.count())
        if search:
            orders = orders.filter(
                Q(customer_id__icontains=search) |
                Q(status__icontains=search)
            )
        if request.user.role_id==3:
            orders=orders.exclude(Q(status="pending")|Q(status="placed")|Q(status="cancelled"))
        if request.user.role_id==4:
            orders=orders.exclude(Q(status="pending")|Q(status="placed")|Q(status="cancelled")|Q(status="confirmed"))
        
        page = self.paginate_queryset(orders)
        serializer = CustomOrderSerializer(page, many=True)

        return self.get_paginated_response(serializer.data)


# =====================================================
# 🟢 ORDER DETAILS
# =====================================================
class orderdetails(GenericAPIView):

    def post(self, request):

        order_id = request.data.get('order_id')

        order = Order.objects.filter(id=order_id).first()

        items = OrderItem.objects.filter(order=str(order_id))

        return Response({
            "data": {
                "order": CustomOrderSerializer(order).data,
                "items": CustomOrderItemSerializer(items, many=True).data
            },
            "response": {"n": 1, "msg": "Order details", "status": "success"}
        })


# =====================================================
# 🟢 CUSTOMER ORDER LIST
# =====================================================
class customerorderlist(GenericAPIView):

    def post(self, request):

        customer_id = request.data.get('customer_id')

        orders = Order.objects.filter(
            customer_id=customer_id,
            isActive=True
        ).order_by('-id')

        serializer = OrderSerializer(orders, many=True)

        return Response({
            "data": serializer.data,
            "response": {"n": 1, "msg": "Customer orders", "status": "success"}
        })


# =====================================================
# 🟢 ORDER STATUS
# =====================================================
class confirmorder(GenericAPIView):

    def post(self, request):

        order_id = request.data.get('order_id')

        order = Order.objects.filter(id=order_id, isActive=True).first()
        if not order:
            return Response({"response": {"n": 0, "msg": "Order not found"}})

        order.status = 'confirmed'
        order.save()

        return Response({"response": {"n": 1, "msg": "Order confirmed"}})


class dispatchorder(GenericAPIView):

    @transaction.atomic
    def post(self, request):

        order_id = request.data.get('order_id')

        order = Order.objects.filter(id=order_id, isActive=True).first()
        if not order:
            return Response({"response": {"n": 0, "msg": "Order not found", "status":"error"}})

        if order.status == "dispatched":
            return Response({"response": {"n": 0, "msg": "Already dispatched", "status":"error"}})

        order_items = OrderItem.objects.filter(order=order.id)

        for item in order_items:
            product_obj=ProductVariant.objects.filter(id=item.product_variant).first()
            if product_obj is None:
                return Response({
                    "response": {
                        "n": 0,
                        "msg": f"Product Variant not found",
                        "status": "error"
                    }
                })
            product_variant_serializer=CustomProductVariantSerializer(product_obj)
            product_unit=product_variant_serializer.data['product_unit_id']
            pack_size=product_variant_serializer.data['pack_size']
            
            required_qty =float(pack_size) * float(item.quantity)
            result=convert_to_base_unit(required_qty,product_unit)
            required_qty_base = result["quantity"]
            
            # 🔥 FETCH ALL AVAILABLE STOCK (FIFO)
            inventory_qs = Inventory.objects.select_for_update().filter(
                stock_id=item.product,
                inventory_type="finished",
                quantity__gt=0,
                isActive=True
            ).order_by("createdAt")

            total_available = (
                inventory_qs.aggregate(total=Sum("quantity"))["total"] or 0
            )
            print("total_available",total_available)
            print("required_qty",required_qty)


            if total_available < required_qty_base:
                return Response({
                    "response": {
                        "n": 0,
                        "msg": f"Insufficient stock for product {item.product_variant}",
                        "status": "error"
                    }
                })

            # 🔥 DEDUCT STOCK BATCH-WISE
            for inv in inventory_qs:

                if required_qty_base <= 0:
                    break

                if inv.quantity >= required_qty_base:

                    inv.quantity -= required_qty_base
                    used_qty = required_qty_base
                    required_qty_base = 0

                else:

                    used_qty = inv.quantity
                    required_qty_base -= inv.quantity
                    inv.quantity = 0

                # InventoryTransaction.objects.create(
                #     inventory=inv.id,
                #     reference_type="dispatch",
                #     reference_id=order.id,
                #     stock_id=inv.stock_id,
                #     transaction_type="OUT",
                #     quantity=used_qty,
                #     batch=inv.batch,
                # )
                inv.save(update_fields=["quantity"])


        # 🔥 UPDATE ORDER STATUS
        order.status = 'dispatched'
        order.save()

        return Response({
            "response": {
                "n": 1,
                "msg": "Order dispatched successfully",
                "status": "success"
            }
        })

class cancelorder(GenericAPIView):

    def post(self, request):

        order_id = request.data.get('order_id')

        order = Order.objects.filter(id=order_id).first()
        order.status = 'cancelled'
        order.save()

        return Response({"response": {"n": 1, "msg": "Order cancelled"}})

class production_ready(GenericAPIView):

    def post(self, request):

        order_id = request.data.get('order_id')

        order = Order.objects.filter(id=order_id).first()
        order.status = 'production-ready'
        order.save()

        return Response({"response": {"n": 1, "msg": "Order Ready For Production"}})
    

class dispatch_ready(GenericAPIView):

    def post(self, request):

        order_id = request.data.get('order_id')

        order = Order.objects.filter(id=order_id).first()
        order.status = 'dispatch-ready'
        order.save()

        return Response({"response": {"n": 1, "msg": "Order Ready For dispatch"}})
class deliverorder(GenericAPIView):

    def post(self, request):

        order_id = request.data.get('order_id')

        order = Order.objects.filter(id=order_id).first()
        order.status = 'delivered'
        order.save()

        return Response({"response": {"n": 1, "msg": "Order delivered"}})


# =====================================================
# 🟢 ADD PAYMENT
# =====================================================
class addpayment(GenericAPIView):

    def post(self, request):

        order_id = request.data.get('order_id')
        amount = to_float(request.data.get('amount'))

        order = Order.objects.filter(id=order_id).first()

        Payment.objects.create(
            order_id=order_id,
            amount=amount,
            payment_mode=request.data.get('payment_mode')
        )

        order.paid_amount += amount
        order.credit_amount = order.total_amount - order.paid_amount
        order.save()

        return Response({
            "response": {"n": 1, "msg": "Payment added", "status": "success"}
        })


# =====================================================
# 🟢 DELETE ORDER (SOFT DELETE)
# =====================================================
class deleteorder(GenericAPIView):

    def post(self, request):

        order_id = request.data.get('order_id')

        order = Order.objects.filter(id=order_id, isActive=True).first()

        if not order:
            return Response({"response": {"n": 0, "msg": "Order not found"}})

        order.isActive = False
        order.save()

        return Response({
            "response": {"n": 1, "msg": "Order deleted", "status": "success"}
        })
        
        
class check_stock_availablity(GenericAPIView):

    def post(self, request):

        order_id = request.data.get("order_id")
        if not order_id:
            return Response({
                "data": {
                    "products": [],
                    "production_required":False,
                },
                "response": {
                    "n": 0,
                    "msg": "Please enter order id"
                }
            })

        order_items = OrderItem.objects.filter(order=order_id)

        if not order_items.exists():
            return Response({
                "data": {
                    "products": [],
                    "production_required":False,
                },
                "response": {
                    "n": 0,
                    "msg": "Order items not found"
                }
            })

        product_data = []
        product_variants = ProductVariant.objects.filter(isActive=True)
        products = Product.objects.filter(isActive=True)
        production_required=False
        for item in order_items:
            ordered_qty = float(item.quantity or 0)
            stock = (Inventory.objects.filter(stock_id=item.product,inventory_type='finished',isActive=True).aggregate(total=Sum("quantity"))["total"] or 0)
            variant = product_variants.filter(id=item.product_variant).first()

            product_name = ""
            product_id = ""
            pack_size = 1
            product_unit = ""
            product_unit_name = ""

            if variant:
                pack_size = float(variant.pack_size or 1)
                product_id = variant.product
                product_obj = products.filter(id=variant.product).first()
                if product_obj:
                    product_name = product_obj.name
                    product_unit = product_obj.unit
                    if product_obj.unit is not None and product_obj.unit !='':
                        unit_obj=UnitMaster.objects.filter(id=product_obj.unit,isActive=True).first()
                        if unit_obj is not None:
                            product_unit_name = unit_obj.short_name
                            
                            
                            
            #convert the order quantity in base unit quantity and check the stock
            pack_size=variant.pack_size
            required_product_qty = float(pack_size) * float(ordered_qty)
            result=convert_to_base_unit(required_product_qty,product_unit)
            required_qty_base = result["quantity"]
            required_product_qty = max(0,required_qty_base - stock)

            if required_product_qty <= 0:
                product_data.append({
                    "product_name": product_name,
                    "product_variant": item.product_variant,
                    "product_id": product_id,
                    "ordered_qty": ordered_qty,
                    "available_stock": stock,
                    "required_qty": 0,
                    "product_unit": product_unit,
                    "product_unit_name": product_unit_name,
                    "pack_size": pack_size,
                })
                continue


                
                
            product_data.append({
                "product_name": product_name,
                "product_variant": item.product_variant,
                "product_id": product_id,
                "ordered_qty": ordered_qty,
                "available_stock": stock,
                "required_qty": required_product_qty,
                "product_unit": product_unit,
                "product_unit_name": product_unit_name,
                "pack_size": pack_size,
            })
            production_required=True

            
            

        return Response({

            "data": {
                "products": product_data,
                "production_required":production_required,
            },

            "response": {
                "n": 1,
                "msg": "Requirement calculated"
            }
        })
    

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        