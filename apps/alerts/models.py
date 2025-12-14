from django.db import models
from apps.core.models import BaseModel
from apps.readings.models import Reading
from apps.sensors.models import Sensor
from apps.nodes.models import Node


class Alert(BaseModel):
    """
    Represents an alert triggered when a reading exceeds a critical threshold.
    """

    class AlertStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        ATTENDED = "attended", "Attended"

    class AlertType(models.TextChoices):
        HIGH_TEMPERATURE = "high_temperature", "High Temperature"
        LOW_HUMIDITY = "low_humidity", "Low Humidity"
        HIGH_PRESSURE = "high_pressure", "High Pressure"
        HIGH_LUMINOSITY = "high_luminosity", "High Luminosity"
        HIGH_WIND = "high_wind", "High Wind"

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

    alert_type = models.CharField(
        max_length=30,
        choices=AlertType.choices,
        verbose_name="Type of alert"
    )

    detected_value = models.FloatField(verbose_name="Detected value")

    status = models.CharField(
        max_length=20,
        choices=AlertStatus.choices,
        default=AlertStatus.PENDING,
        verbose_name="Alert status"
    )

    class Meta:
        verbose_name = "Alert"
        verbose_name_plural = "Alerts"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Alert {self.alert_type} @ {self.node.name}: {self.detected_value}"
