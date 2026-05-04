from django.db import models
from helpers.models import TrackingModel
# Create your models here.

class Vehicle(TrackingModel):
    number = models.CharField(max_length=50)
    capacity = models.FloatField()

class LogisticsOrder(TrackingModel):
    source = models.CharField(max_length=200)
    destination = models.CharField(max_length=200)
    vehicle =  models.CharField(max_length=200)
    status = models.CharField(max_length=50)


class Delivery(TrackingModel):
    order = models.CharField(max_length=200)
    agent = models.CharField(max_length=200)
    status = models.CharField(max_length=50)
    delivered_at = models.DateTimeField(null=True, blank=True)