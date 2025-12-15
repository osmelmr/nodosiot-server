from django.db import models
from apps.readings.models import Reading
from apps.sensors.models import Sensor
from apps.nodes.models import Node


class Alert(models.Model):
    """
    Represents an alert triggered when a reading exceeds a critical threshold.
    """

    class AlertStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        ATTENDED = "attended", "Attended"

    class AlertType(models.TextChoices):
        HIGH = "high", "High"
        LOW = "low", "Low"

    alert_type = models.CharField(
        max_length=20,
        choices=AlertType.choices,
        verbose_name="Alert type"
    )
    
    sensor = models.ForeignKey(
        Sensor,
        on_delete=models.CASCADE,
        related_name="alerts",
        verbose_name="Sensor"
    )

    node = models.ForeignKey(
        Node,
        on_delete=models.CASCADE,
        related_name="alerts",
        verbose_name="Node"
    )

    reading = models.ForeignKey(
        Reading,
        on_delete=models.CASCADE,
        related_name="alerts",
        verbose_name="Reading"
    )

    detected_value = models.FloatField(verbose_name="Detected value")

    status = models.CharField(
        max_length=20,
        choices=AlertStatus.choices,
        default=AlertStatus.PENDING,
        verbose_name="Alert status"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        verbose_name="Creation date"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Last update"
    )

    class Meta:
        verbose_name = "Alert"
        verbose_name_plural = "Alerts"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Alert {self.alert_type} @ {self.node.name}: {self.detected_value}"
