from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .models import Reading
from .serializers import ReadingSerializer
from apps.core.permissions import IsAdminOrReadOnly
from apps.alerts.models import Alert


@api_view(['GET', 'POST'])
@permission_classes([IsAdminOrReadOnly])
def reading_list_create(request):
    """
    List all readings or create a new reading.
    Auto-generate alerts based on validation_status.
    """
    if request.method == 'GET':
        readings = Reading.objects.all()
        serializer = ReadingSerializer(readings, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = ReadingSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Guardamos la lectura TAL CUAL viene
        reading = serializer.save()

        alert = None

        # ----------------------------------------
        # Creación de alerta basada en validation_status
        # ----------------------------------------
        if reading.validation_status in (
            Reading.ValidationStatus.HIGH,
            Reading.ValidationStatus.LOW,
        ):
            alert = Alert.objects.create(
                sensor=reading.sensor,
                node=reading.node,
                reading=reading,
                alert_type=reading.validation_status,  # 'high' o 'low'
                detected_value=reading.value,
                status=Alert.AlertStatus.PENDING
            )

        response_data = ReadingSerializer(reading).data

        if alert:
            response_data["alert"] = {
                "id": alert.id,
                "alert_type": alert.alert_type,
                "status": alert.status,
                "detected_value": alert.detected_value,
            }

        return Response(response_data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAdminOrReadOnly])
def reading_detail(request, pk):
    """
    Retrieve, update, or delete a reading by pk.
    """
    try:
        reading = Reading.objects.get(pk=pk)
    except Reading.DoesNotExist:
        return Response({"error": "Reading not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ReadingSerializer(reading)
        return Response(serializer.data)
    
    if request.method in ['PATCH', 'DELETE']:
        if reading.node.user_id != request.user.id:
            return Response(
                {"detail": "You do not own the node associated with this reading."},
                status=status.HTTP_403_FORBIDDEN
            )
        
    if request.method == 'PATCH':
        serializer = ReadingSerializer(reading, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        reading.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# -----------------------------
# Lecturas recientes filtrables por tiempo, nodo y sensor
# -----------------------------
@api_view(['GET'])
@permission_classes([IsAdminOrReadOnly])
def latest_readings(request):
    interval = int(request.query_params.get('interval', 60))
    unit = request.query_params.get('unit', 'minutes')
    node_id = request.query_params.get('node_id')
    sensor_id = request.query_params.get('sensor_id')

    # Calculamos la fecha/hora límite
    if unit == 'seconds':
        time_threshold = timezone.now() - timedelta(seconds=interval)
    else:  # default a minutos
        time_threshold = timezone.now() - timedelta(minutes=interval)

    readings = Reading.objects.filter(timestamp__gte=time_threshold)

    if node_id:
        readings = readings.filter(node__id=node_id)
    if sensor_id:
        readings = readings.filter(sensor__id=sensor_id)

    readings = readings.order_by('-timestamp')
    serializer = ReadingSerializer(readings, many=True)
    return Response(serializer.data)
