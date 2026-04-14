from django.db import models
from helpers.models import TrackingModel

# Orders/models.py

from django.conf import settings

class Order(TrackingModel):
    STATUS = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
    )

    customer = models.CharField(max_length=20)
    total_amount = models.FloatField()
    status = models.CharField(max_length=20, choices=STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

class OrderItem(TrackingModel):
    order = models.CharField(max_length=20)
    product_variant = models.CharField(max_length=20,)
    quantity = models.IntegerField()
    price = models.FloatField()


class ProcurementOrder(TrackingModel):
    vendor =models.CharField(max_length=20)
    date = models.DateField()
    total_quantity = models.FloatField()

class ProcurementItem(TrackingModel):
    procurement = models.CharField(max_length=20)
    product_name = models.CharField(max_length=100)  # Milk
    quantity = models.FloatField()
    fat = models.FloatField()
    snf = models.FloatField()
    price = models.FloatField()



class ProcessingBatch(TrackingModel):
    batch_number = models.CharField(max_length=100, unique=True)
    input_quantity = models.FloatField()  # milk liters
    output_quantity = models.FloatField()  # final product
    created_at = models.DateTimeField(auto_now_add=True)

class BatchOutput(TrackingModel):
    batch = models.CharField(max_length=20)
    product_variant = models.CharField(max_length=20)
    quantity = models.FloatField()


class LogisticsOrder(models.Model):
    source = models.CharField(max_length=200)
    destination = models.CharField(max_length=200)
    vehicle =  models.CharField(max_length=200)
    status = models.CharField(max_length=50)


class Delivery(models.Model):
    order = models.CharField(max_length=200)
    agent = models.CharField(max_length=200)
    status = models.CharField(max_length=50)
    delivered_at = models.DateTimeField(null=True, blank=True)