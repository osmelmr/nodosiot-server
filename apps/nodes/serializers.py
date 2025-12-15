from rest_framework import serializers
from .models import Node


class NodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Node
        fields = (
            "id",
            "name",
            "description",
            "location",
            "latitude",
            "longitude",
            "is_active",
            "is_deleted",
            "created_at",
            "updated_at",
            "sampling_interval",
        )
        read_only_fields = (
            "id",
            "is_deleted",
            "created_at",
            "updated_at",
        )
