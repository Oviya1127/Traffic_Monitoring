from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

# Model for detected objects
class DetectedObject(models.Model):
    object_type = models.CharField(max_length=100)
    confidence = models.FloatField()
    location = models.CharField(max_length=255, default="Unknown")  # ✅ Default added
    image = models.ImageField(upload_to="detections/", blank=True, null=True)  # ✅ Allowed NULL
    timestamp = models.DateTimeField(auto_now_add=True)
    new_field = models.CharField(max_length=100, default="DefaultValue")  

    def __str__(self):
        return f"{self.object_type} - {self.confidence:.2f}"


# Model for storing traffic violations
class Violation(models.Model):
    VIOLATION_TYPES = [
        ('speeding', 'Speeding'),
        ('signal_jump', 'Signal Jump'),
        ('wrong_lane', 'Wrong Lane'),
        ('other', 'Other')
    ]

    violation_type = models.CharField(max_length=50, choices=VIOLATION_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=255, default="Unknown")  
    vehicle_number = models.CharField(max_length=20, blank=True, null=True)
    detected_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    image = models.ImageField(upload_to='violations/', blank=True, null=True)

    def __str__(self):
        return f"{self.violation_type} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"


# Model for tracking driver behavior incidents
class DriverBehavior(models.Model):
    BEHAVIOR_TYPES = [
        ('reckless', 'Reckless Driving'),
        ('drunk', 'Drunk Driving'),
        ('distracted', 'Distracted Driving'),
        ('other', 'Other')
    ]

    behavior_type = models.CharField(max_length=50, choices=BEHAVIOR_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=255, default="Unknown", blank=True, null=True)  
    vehicle_number = models.CharField(max_length=20, blank=True, null=True)
    detected_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    image = models.ImageField(upload_to='driver_behavior/', blank=True, null=True)

    def __str__(self):
        return f"{self.behavior_type} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
