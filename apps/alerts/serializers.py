from rest_framework import serializers
from .models import Alert


class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = (
            "id",
            "uuid",
            "sensor",
            "node",
            "reading",
            "alert_type",
            "detected_value",
            "status",
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
