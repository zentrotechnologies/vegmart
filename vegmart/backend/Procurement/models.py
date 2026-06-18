from django.db import models
from helpers.models import TrackingModel



class RawProductMaster(TrackingModel): #Raw Products
    item_code = models.CharField(max_length=50)
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)  # milk / additives / utilities
    unit = models.CharField(max_length=20)
    is_milk = models.BooleanField(default=False)

class RecipeMaster(TrackingModel): #Recipe
    recipe_code = models.CharField(max_length=50)
    recipe_name = models.CharField(max_length=200)
    version = models.IntegerField(default=1)
    standard_output_qty = models.FloatField(
        help_text="Example: 100 Kg Paneer"
    )
    output_unit = models.CharField(
        max_length=20,
        default='kg'
    )
    # 🔹 FINISHED PRODUCT (curd, paneer, etc.)
    product = models.CharField(max_length=50)
    remarks = models.TextField(
        null=True,
        blank=True
    )
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )   
    class Meta:
        unique_together = ('recipe_code', 'version')


class RecipeRawmaterial(TrackingModel):
    recipe_id = models.CharField(max_length=20)
    raw_product_id = models.CharField(max_length=20)
    quantity = models.FloatField()
    unit = models.CharField(max_length=20)
    wastage_percent = models.FloatField(default=0)
    remarks = models.CharField(max_length=200,blank=True,null=True)
















class ProcurementEntry(TrackingModel):
    supplier_id = models.CharField(max_length=20)
    order_id = models.CharField(max_length=20, null=True, blank=True)
    total_amount = models.FloatField(default=0)
    paid_amount = models.FloatField(default=0)
    credit_amount = models.FloatField(default=0)
    status = models.CharField(max_length=20, default="processing")

class ProcurementRawmaterial(TrackingModel):
    procurement = models.CharField(max_length=20)
    raw_material_id = models.CharField(max_length=100)
    quantity = models.FloatField()
    unit = models.CharField(max_length=20)
    fat = models.FloatField(null=True, blank=True)
    snf = models.FloatField(null=True, blank=True)
    rate = models.FloatField(default=0)
    total = models.FloatField(default=0)

class ProcurementOutput(TrackingModel):
    recipe_id = models.CharField(max_length=20)
    procurement = models.CharField(max_length=20)
    raw_product_id = models.CharField(max_length=20)
    quantity = models.FloatField()
    unit = models.CharField(max_length=20)
    is_primary_output = models.BooleanField(default=True)



