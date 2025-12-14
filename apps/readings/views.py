from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta

from .models import Reading
from .serializers import ReadingSerializer
from apps.core.permissions import IsAdminOrReadOnly
from apps.alerts.models import Alert


# -----------------------------
# CRUD y POST de lecturas
# -----------------------------
@api_view(['GET', 'POST'])
@permission_classes([IsAdminOrReadOnly])
def reading_list_create(request):
    """
    List all readings or create a new reading.
    Auto-generate alerts if value exceeds sensor thresholds.
    """
    if request.method == 'GET':
        readings = Reading.objects.filter(is_deleted=False)
        serializer = ReadingSerializer(readings, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = ReadingSerializer(data=request.data)
        if serializer.is_valid():
            reading = serializer.save()

            # ----------------------------------------
            # Detección automática de alertas
            # ----------------------------------------
            sensor = reading.sensor
            alert_created = False

            if sensor.max_value is not None and reading.value > sensor.max_value:
                Alert.objects.create(
                    sensor=sensor,
                    node=reading.node,
                    alert_type=f"{sensor.sensor_type} alto",
                    detected_value=reading.value,
                    status="pending"
                )
                alert_created = True

            if sensor.min_value is not None and reading.value < sensor.min_value:
                Alert.objects.create(
                    sensor=sensor,
                    node=reading.node,
                    alert_type=f"{sensor.sensor_type} bajo",
                    detected_value=reading.value,
                    status="pending"
                )
                alert_created = True

            response_data = serializer.data
            if alert_created:
                response_data['alert'] = "Threshold exceeded - Alert created"

            return Response(response_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAdminOrReadOnly])
def reading_detail(request, uuid):
    """
    Retrieve, update, or delete a reading by UUID.
    """
    try:
        reading = Reading.objects.get(uuid=uuid, is_deleted=False)
    except Reading.DoesNotExist:
        return Response({"error": "Reading not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ReadingSerializer(reading)
        return Response(serializer.data)

    if request.method == 'PATCH':
        serializer = ReadingSerializer(reading, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        reading.is_deleted = True
        reading.save(update_fields=['is_deleted'])
        return Response(status=status.HTTP_204_NO_CONTENT)


# -----------------------------
# Lecturas recientes filtrables por tiempo, nodo y sensor
# -----------------------------
@api_view(['GET'])
@permission_classes([IsAdminOrReadOnly])
def latest_readings(request):
    """
    Devuelve lecturas recientes filtradas por nodo, sensor y tiempo.
    Query params:
      - interval: cantidad de tiempo hacia atrás (default=60)
      - unit: 'minutes' o 'seconds' (default='minutes')
      - node_id: UUID del nodo (opcional)
      - sensor_id: UUID del sensor (opcional)
    """
    interval = int(request.query_params.get('interval', 60))
    unit = request.query_params.get('unit', 'minutes')
    node_id = request.query_params.get('node_id')
    sensor_id = request.query_params.get('sensor_id')

    # Calculamos la fecha/hora límite
    if unit == 'seconds':
        time_threshold = timezone.now() - timedelta(seconds=interval)
    else:  # default a minutos
        time_threshold = timezone.now() - timedelta(minutes=interval)

    readings = Reading.objects.filter(is_deleted=False, timestamp__gte=time_threshold)

    if node_id:
        readings = readings.filter(node__uuid=node_id)
    if sensor_id:
        readings = readings.filter(sensor__uuid=sensor_id)

    readings = readings.order_by('-timestamp')
    serializer = ReadingSerializer(readings, many=True)
    return Response(serializer.data)
