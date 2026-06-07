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
        order_items = []

        # 🔥 PRICE CALCULATION
        for item in items:

            variant_id = item.get('product_variant')
            qty = int(item.get('quantity'))
            price = int(item.get('price'))

            # 🔥 CUSTOMER PRICING
            # cp = CustomerPricing.objects.filter(
            #     customer_id=customer_id,
            #     product_variant_id=variant_id
            # ).first()
            variant = ProductVariant.objects.filter(id=variant_id).first()

            # if cp:
            #     price = cp.custom_price
            # else:
            #     price = variant.b2b_price if variant else 0

            total = price * qty
            total_amount += total

            order_items.append({
                "variant": variant_id,
                "qty": qty,
                "price": price,
                "product":variant.product
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
                price=i['price']
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

    pagination_class = CustomPagination

    def post(self, request):

        search = request.data.get('search')

        orders = Order.objects.filter(isActive=True).order_by('-id')

        if search:
            orders = orders.filter(
                Q(customer_id__icontains=search) |
                Q(status__icontains=search)
            )

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

            required_qty = item.quantity

            # 🔥 FETCH ALL AVAILABLE STOCK (FIFO)
            inventory_qs = Inventory.objects.filter(
                product_variant=item.product_variant,
                inventory_type='finished',
                quantity__gt=0
            ).order_by('createdAt')

            total_available = sum([i.quantity for i in inventory_qs])

            if total_available < required_qty:
                return Response({
                    "response": {
                        "n": 0,
                        "msg": f"Insufficient stock for product {item.product_variant}",
                        "status": "error"
                    }
                })

            # 🔥 DEDUCT STOCK BATCH-WISE
            for inv in inventory_qs:

                if required_qty <= 0:
                    break

                if inv.quantity >= required_qty:
                    # FULLY SATISFY FROM THIS BATCH
                    inv.quantity -= required_qty
                    used_qty = required_qty
                    required_qty = 0
                else:
                    # USE FULL BATCH
                    used_qty = inv.quantity
                    required_qty -= inv.quantity
                    inv.quantity = 0

                inv.save()



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