from django.db import models
from helpers.models import TrackingModel



class ProcurementItemMaster(TrackingModel):
    item_code = models.CharField(max_length=50)
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)  # milk / additives / utilities
    unit = models.CharField(max_length=20)
    is_milk = models.BooleanField(default=False)

class ProcurementToProductMapping(TrackingModel):

    # 🔹 RAW ITEM (milk, SMP, etc.)
    procurement_item = models.CharField(max_length=50)
    # 🔹 FINISHED PRODUCT (curd, paneer, etc.)
    product = models.CharField(max_length=50)

    # 🔹 conversion logic
    conversion_factor = models.FloatField()
    wastage_percent = models.FloatField(default=0)

    # optional (very useful)
    priority = models.IntegerField(default=1)




# ================= HEADER =================
class ProcurementEntry(TrackingModel):
    supplier_id = models.CharField(max_length=20)
    order_id = models.CharField(max_length=20, null=True, blank=True)
    total_amount = models.FloatField(default=0)
    paid_amount = models.FloatField(default=0)
    credit_amount = models.FloatField(default=0)
    status = models.CharField(max_length=20, default="processing")


# ================= CHILD =================
class ProcurementProducts(TrackingModel):
    procurement = models.CharField(max_length=20)
    product_id = models.CharField(max_length=20)
    quantity = models.FloatField()


# ================= CHILD =================
class ProcurementItem(TrackingModel):

    procurement = models.CharField(max_length=20)
    procurement_item_id = models.CharField(max_length=100)
    quantity = models.FloatField()
    unit = models.CharField(max_length=20)
    fat = models.FloatField(null=True, blank=True)
    snf = models.FloatField(null=True, blank=True)
    rate = models.FloatField(default=0)
    total = models.FloatField(default=0)



class ProcurementOutput(TrackingModel):

    procurement = models.CharField(max_length=20)

    product_variant_id = models.CharField(max_length=20)

    quantity = models.FloatField()



