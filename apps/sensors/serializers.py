from rest_framework import serializers
from .models import Sensor

class SensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sensor
        fields = (
            "id",
            "node",
            "name",
            "sensor_type",
            "model",
            "unit",
            "is_active",
            "is_deleted",
        )
        read_only_fields = (
            "id",
            "is_deleted",
        )
