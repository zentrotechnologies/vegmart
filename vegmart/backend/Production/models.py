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


