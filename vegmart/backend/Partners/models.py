from django.db import models
from helpers.models import TrackingModel



class Vendor(TrackingModel):
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=15)
    address = models.TextField()

    
class DeliveryAgent(TrackingModel):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)