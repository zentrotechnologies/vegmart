from django.db import models
from helpers.models import *
# Create your models here.



class Inventory(TrackingModel):
    warehouse = models.CharField(max_length=100)
    product_variant = models.CharField(max_length=100)
    quantity = models.FloatField()