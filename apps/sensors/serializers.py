from rest_framework import serializers
from .models import Sensor


class SensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sensor
        fields = (
            "id",
            "uuid",
            "node",
            "name",
            "sensor_type",
            "model",
            "unit",
            "is_active",
            "is_deleted",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "uuid",
            "is_deleted",
            "created_at",
            "updated_at",
        )
