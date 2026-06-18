from django.db import models
from helpers.models import TrackingModel

# Orders/models.py

from django.conf import settings

# 1	Placed or Pending
# 2	Confirmed
# 3	Procurememt
# 4	Production Ready
# 5	Production
# 6	Dispatch Ready
# 7	Dispatched
# 8	Delivered
class Order(TrackingModel):
    customer_id = models.CharField(max_length=20)

    payment_mode = models.CharField(max_length=50)  # cash / credit / online

    total_amount = models.FloatField()
    paid_amount = models.FloatField(default=0)
    credit_amount = models.FloatField(default=0)

    due_date = models.DateField(null=True, blank=True)

    status = models.CharField(max_length=20, default='pending')

class OrderItem(TrackingModel):
    order = models.CharField(max_length=20)
    product_variant = models.CharField(max_length=20,)
    product = models.CharField(max_length=20,)
    quantity = models.IntegerField()
    price = models.FloatField()

class CustomerPricing(TrackingModel):
    customer_id = models.CharField(max_length=20)
    product_variant_id = models.CharField(max_length=20)

    custom_price = models.FloatField()

class Payment(TrackingModel):
    order_id = models.CharField(max_length=20)

    amount = models.FloatField()
    payment_mode = models.CharField(max_length=50)

    payment_date = models.DateTimeField(auto_now_add=True)





























