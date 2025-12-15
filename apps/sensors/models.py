from django.db import models
from apps.core.models import BaseModel
from apps.nodes.models import Node


class Sensor(BaseModel):
    """
    Represents a physical sensor connected to a Node.
    """

    class SensorTypes(models.TextChoices):
        TEMPERATURE = "temperature", "Temperature"
        HUMIDITY = "humidity", "Humidity"
        PRESSURE = "pressure", "Pressure"
        LUMINOSITY = "luminosity", "Luminosity"
        WIND = "wind", "Wind"

    node = models.ForeignKey(
        Node,
        on_delete=models.CASCADE,
        related_name="sensors",
        verbose_name="Node"
    )

    name = models.CharField(
        max_length=100,
        verbose_name="Sensor name"
    )

    sensor_type = models.CharField(
        max_length=20,
        choices=SensorTypes.choices,
        verbose_name="Sensor type"
    )

    model = models.CharField(
        max_length=50,
        verbose_name="Sensor model"
    )

    unit = models.CharField(
        max_length=10,
        verbose_name="Unit of measure"
    )
    
    class Meta:
        verbose_name = "Sensor"
        verbose_name_plural = "Sensors"
        unique_together = ("node", "name")  # No dos sensores con el mismo nombre en el mismo nodo

    def __str__(self):
        return f"{self.name} ({self.sensor_type})"
