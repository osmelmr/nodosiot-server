from django.db import models
from apps.core.models import BaseModel
from apps.sensors.models import Sensor
from apps.nodes.models import Node


class Reading(BaseModel):
    """
    Represents a measurement reading from a sensor at a specific node.
    """

    class ValidationStatus(models.TextChoices):
        VALID = "valid", "Valid"
        OUT_OF_RANGE = "out_of_range", "Out of Range"
        ERROR = "error", "Error"

    sensor = models.ForeignKey(
        Sensor,
        on_delete=models.CASCADE,
        related_name="readings",
        verbose_name="Sensor"
    )

    node = models.ForeignKey(
        Node,
        on_delete=models.CASCADE,
        related_name="readings",
        verbose_name="Node"
    )

    value = models.FloatField(verbose_name="Sensor value")

    timestamp = models.DateTimeField(
        verbose_name="Timestamp of the reading"
    )

    validation_status = models.CharField(
        max_length=20,
        choices=ValidationStatus.choices,
        default=ValidationStatus.VALID,
        verbose_name="Validation status"
    )

    class Meta:
        verbose_name = "Reading"
        verbose_name_plural = "Readings"
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.sensor.name} @ {self.node.name}: {self.value} ({self.timestamp})"
