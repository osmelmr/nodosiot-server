from django.db import models
from apps.core.models import BaseModel


class Node(BaseModel):
    """
    Physical IoT node (Arduino / Gateway).
    """

    name = models.CharField(
        max_length=100,
        verbose_name="Node name"
    )

    description = models.TextField(
        blank=True,
        verbose_name="Description"
    )

    sampling_interval = models.IntegerField(default=10, verbose_name="Sampling interval (seconds)")

    location = models.CharField(
        max_length=255,
        verbose_name="Location"
    )

    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name="Latitude"
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name="Longitude"
    )

    class Meta:
        verbose_name = "Node"
        verbose_name_plural = "Nodes"

    def __str__(self):
        return f"{self.name} ({self.location})"
