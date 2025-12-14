from rest_framework import serializers
from .models import Reading


class ReadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reading
        fields = (
            "id",
            "uuid",
            "sensor",
            "node",
            "value",
            "timestamp",
            "validation_status",
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
