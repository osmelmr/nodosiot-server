from rest_framework import serializers
from .models import Reading


class ReadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reading
        fields = (
            "id",
            "sensor",
            "node",
            "value",
            "timestamp",
            "validation_status",
            "created_at",
        )
        read_only_fields = (
            "id",
            "created_at",
        )
