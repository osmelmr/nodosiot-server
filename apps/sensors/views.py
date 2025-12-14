from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Sensor
from .serializers import SensorSerializer
from apps.core.permissions import IsAdminOrReadOnly

# -----------------------------
# CRUD de sensores
# -----------------------------

@api_view(['GET', 'POST'])
@permission_classes([IsAdminOrReadOnly])
def sensor_list_create(request):
    """
    List all sensors or create a new sensor (admin only for create).
    """
    if request.method == 'GET':
        sensors = Sensor.objects.filter(is_deleted=False)
        serializer = SensorSerializer(sensors, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = SensorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAdminOrReadOnly])
def sensor_detail(request, uuid):
    """
    Retrieve, update, or delete a sensor by UUID.
    """
    try:
        sensor = Sensor.objects.get(uuid=uuid, is_deleted=False)
    except Sensor.DoesNotExist:
        return Response({"error": "Sensor not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = SensorSerializer(sensor)
        return Response(serializer.data)

    if request.method == 'PATCH':
        serializer = SensorSerializer(sensor, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        sensor.is_deleted = True
        sensor.save(update_fields=['is_deleted'])
        return Response(status=status.HTTP_204_NO_CONTENT)
