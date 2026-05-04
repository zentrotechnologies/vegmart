from django.db import models
from helpers.models import TrackingModel
# Create your models here.

class AuditLog(TrackingModel):
    user_id = models.CharField(max_length=20)

    action = models.CharField(max_length=100)  # price_override / due_date_change

    old_value = models.TextField()
    new_value = models.TextField()

    timestamp = models.DateTimeField(auto_now_add=True)