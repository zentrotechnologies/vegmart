from django.db import models
from helpers.models import TrackingModel

class Category(TrackingModel):
    name = models.CharField(max_length=100)

class SubCategory(TrackingModel):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100) #dont use forignkeys

class Product(TrackingModel):
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=100, unique=True)
    hsn_code = models.CharField(max_length=20)
    category = models.CharField(max_length=100)
    sub_category = models.CharField(max_length=100)
    brand = models.CharField(max_length=100)
    unit = models.CharField(max_length=100)

class ProductVariant(TrackingModel):
    image = models.FileField(upload_to='products/variants/images/', blank=True, null=True,verbose_name='media Image')
    product = models.CharField(max_length=100)
    pack_size = models.CharField(max_length=50)   # 500ml, 1kg
    pack_type = models.CharField(max_length=50)   # pouch, bottle
    fat = models.FloatField(null=True, blank=True)
    snf = models.FloatField(null=True, blank=True)
    gst_rate = models.FloatField()
    mrp = models.FloatField()
    b2b_price = models.FloatField()


class UnitMaster(TrackingModel):

    unit_name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=20)
    parent_unit = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    conversion_factor = models.FloatField(
        default=1
    )