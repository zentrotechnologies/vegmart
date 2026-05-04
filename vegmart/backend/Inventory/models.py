from django.db import models
from helpers.models import *
# Create your models here.

class Warehouse(TrackingModel):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)

class Batch(TrackingModel):
    batch_number = models.CharField(max_length=100)
    product_variant = models.CharField(max_length=100)
    expiry_date = models.DateField()
    quantity = models.FloatField()

class Inventory(TrackingModel):
    
    
    INVENTORY_TYPE_CHOICES = [
            ('raw', 'Raw Material'),
            ('finished', 'Finished Goods'),
            ('transit', 'Transit'),
        ]
    warehouse = models.CharField(max_length=100)
    product_variant = models.CharField(max_length=100)
    quantity = models.FloatField()
    batch = models.CharField(max_length=100)
    inventory_type = models.CharField(
        max_length=20,
        choices=INVENTORY_TYPE_CHOICES,
        default='finished'
    )


class StockMovement(TrackingModel):

    MOVEMENT_TYPE = [
        ('in', 'Stock In'),       # procurement / production
        ('out', 'Stock Out'),     # sales
        ('transfer', 'Transfer'), # warehouse movement
    ]

    product_variant = models.CharField(max_length=20,)

    from_warehouse = models.CharField(max_length=20,)

    to_warehouse = models.CharField(max_length=20,)

    quantity = models.FloatField()

    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPE)

    reference_id = models.CharField(max_length=100, null=True, blank=True)
    # example:
    # procurement_id / order_id / batch_id

    remarks = models.TextField(null=True, blank=True)

