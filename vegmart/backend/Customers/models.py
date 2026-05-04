from django.db import models
from helpers.models import TrackingModel



# Create your models here.
class Customer(TrackingModel):
    name = models.CharField(max_length=200)
    mobile = models.CharField(max_length=15)

    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, null=True, blank=True)

    area = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)

    gst_number = models.CharField(max_length=50, null=True, blank=True)

    customer_type = models.CharField(max_length=50)  # B2B / B2C

    default_credit_days = models.IntegerField(default=0)
    outstanding_balance = models.FloatField(default=0)