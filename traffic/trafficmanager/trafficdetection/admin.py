from django.contrib import admin
from .models import DetectedObject, Violation, DriverBehavior

@admin.register(DetectedObject)
class DetectedObjectAdmin(admin.ModelAdmin):
    list_display = ('object_type', 'confidence', 'timestamp')
    search_fields = ('object_type',)
    list_filter = ('timestamp',)

@admin.register(Violation)
class ViolationAdmin(admin.ModelAdmin):
    list_display = ('violation_type', 'timestamp', 'vehicle_number')
    search_fields = ('violation_type', 'vehicle_number')
    list_filter = ('timestamp', 'violation_type')

@admin.register(DriverBehavior)
class DriverBehaviorAdmin(admin.ModelAdmin):
    list_display = ('behavior_type', 'timestamp', 'vehicle_number')
    search_fields = ('behavior_type', 'vehicle_number')
    list_filter = ('timestamp', 'behavior_type')
