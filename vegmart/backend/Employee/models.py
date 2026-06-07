from django.db import models
from helpers.models import TrackingModel
# Create your models here.
class EmployeeMaster(TrackingModel):
    EMPLOYEE_STATUS = (
        ("ACTIVE", "Active"),
        ("INACTIVE", "Inactive"),
        ("RESIGNED", "Resigned"),
        ("TERMINATED", "Terminated"),
    )

    GENDER_CHOICES = (
        ("MALE", "Male"),
        ("FEMALE", "Female"),
        ("OTHER", "Other"),
    )

    # Basic Details
    employee_code = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    full_name = models.CharField(max_length=255)

    # Contact Details
    email = models.EmailField(unique=True)
    mobile_number = models.CharField(max_length=15, unique=True)
    alternate_mobile = models.CharField(max_length=15, blank=True, null=True)

    # Employment Details
    designation = models.CharField(max_length=100)
    department = models.CharField(max_length=100, blank=True, null=True)
    role = models.CharField(max_length=100)

    joining_date = models.DateField(blank=True, null=True)
    relieving_date = models.DateField(blank=True, null=True)

    reporting_manager = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subordinates"
    )

    # Personal Details
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        blank=True,
        null=True
    )

    date_of_birth = models.DateField(blank=True, null=True)

    # Address
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)

    # Status
    status = models.CharField(
        max_length=20,
        choices=EMPLOYEE_STATUS,
        default="ACTIVE"
    )

    # Authentication Mapping
    user_id = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = "employee_master"
        ordering = ["full_name"]

    def __str__(self):
        return f"{self.employee_code} - {self.full_name}"
