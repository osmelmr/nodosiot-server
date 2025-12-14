from rest_framework import serializers
from .models import Node


class NodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Node
        fields = (
            "id",
            "uuid",
            "name",
            "description",
            "location",
            "latitude",
            "longitude",
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
