from django.db import models
from helpers.models import TrackingModel
# Create your models here.

class ProcessingBatch(TrackingModel):
    batch_number = models.CharField(max_length=100, unique=True)
    input_quantity = models.FloatField()  # milk liters
    output_quantity = models.FloatField()  # final product
    created_at = models.DateTimeField(auto_now_add=True)

class BatchOutput(TrackingModel):
    batch = models.CharField(max_length=20)
    product_variant = models.CharField(max_length=20)
    quantity = models.FloatField()


class ProductionEntry(TrackingModel):
    PRODUCTION_TYPE = (
        ("manual", "Manual"),
        ("order", "Order Based"),
    )

    production_type = models.CharField(
        max_length=20,
        choices=PRODUCTION_TYPE,
        default="manual"
    )
    order_id = models.CharField(max_length=20, blank=True, null=True)

    recipe_id = models.CharField(max_length=20)

    product_id = models.CharField(max_length=20)

    batch = models.CharField(max_length=100)

    planned_quantity = models.FloatField()

    planned_unit = models.CharField(max_length=20)

    actual_quantity = models.FloatField(default=0)

    actual_unit = models.CharField(max_length=20)

    start_time = models.DateTimeField(null=True, blank=True)

    end_time = models.DateTimeField(null=True, blank=True)

    remarks = models.TextField(blank=True, null=True)
    warehouse = models.CharField(max_length=100, default="0")
    STATUS = (
        ("draft","Draft"),
        ("started","Started"),
        ("completed","Completed"),
        ("cancelled","Cancelled")
    )

    status = models.CharField(max_length=20, choices=STATUS, default="started")
    
    
class ProductionInput(TrackingModel):

    production = models.CharField(max_length=20)

    raw_product_id = models.CharField(max_length=20)

    inventory_batch = models.CharField(max_length=100)

    quantity = models.FloatField()

    unit = models.CharField(max_length=20)

    wastage = models.FloatField(default=0)
    
    
class ProductionOutput(TrackingModel):

    production = models.CharField(max_length=20)

    product_id = models.CharField(max_length=20)

    quantity = models.FloatField()

    unit = models.CharField(max_length=20)

    inventory_batch = models.CharField(max_length=100)

    is_primary = models.BooleanField(default=True)
    
    
class ProductionWastage(TrackingModel):

    production = models.CharField(max_length=20)

    raw_product_id = models.CharField(max_length=20)

    quantity = models.FloatField()

    unit = models.CharField(max_length=20)

    reason = models.CharField(max_length=200)
    
    
    
    
class InventoryTransaction(TrackingModel):

    inventory = models.CharField(max_length=20)

    reference_type = models.CharField(max_length=30)

    reference_id = models.CharField(max_length=30)

    transaction = models.CharField(max_length=20)

    quantity = models.FloatField()

    unit = models.CharField(max_length=20)
    
    
    
    