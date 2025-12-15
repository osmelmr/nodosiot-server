from django.db import models
from django.contrib.auth import get_user_model
from apps.core.models import BaseModel

User = get_user_model()

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
    user = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,  # no elimina el nodo físicamente
        related_name="nodes"
    )
    class Meta:
        verbose_name = "Node"
        verbose_name_plural = "Nodes"

    def __str__(self):
        return f"{self.name} ({self.location})"
