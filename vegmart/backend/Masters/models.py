from django.db import models
from helpers.models import TrackingModel

# Create your models here.

class Warehouse(TrackingModel):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)


class Vendor(TrackingModel):
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=15)
    address = models.TextField()

class Vehicle(models.Model):
    number = models.CharField(max_length=50)
    capacity = models.FloatField()
    
class DeliveryAgent(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)

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

class ProductVariant(TrackingModel):
    product = models.CharField(max_length=100)
    pack_size = models.CharField(max_length=50)   # 500ml, 1kg
    pack_type = models.CharField(max_length=50)   # pouch, bottle
    fat = models.FloatField(null=True, blank=True)
    snf = models.FloatField(null=True, blank=True)
    gst_rate = models.FloatField()
    mrp = models.FloatField()
    b2b_price = models.FloatField()


class Batch(models.Model):
    batch_number = models.CharField(max_length=100)
    product_variant = models.CharField(max_length=100)
    expiry_date = models.DateField()
    quantity = models.FloatField()