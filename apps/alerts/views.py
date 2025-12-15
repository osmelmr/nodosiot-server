# apps/alerts/views.py

from django.utils.dateparse import parse_datetime
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Alert
from .serializers import AlertSerializer


# -----------------------------
# Alertas - Listado y creación
# -----------------------------

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def alert_list_create(request):
    """
    List all alerts or create a new alert.
    """
    if request.method == 'GET':
        # ELIMINAR: .filter(is_deleted=False) - usar todos
        alerts = Alert.objects.all()  # <-- CAMBIADO
        serializer = AlertSerializer(alerts, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = AlertSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# -----------------------------
# Alertas - Detalle
# -----------------------------

@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def alert_detail(request, pk):
    """
    Retrieve, update, or delete an alert by pk.
    """
    try:
        # ELIMINAR: , is_deleted=False - buscar todos
        alert = Alert.objects.get(pk=pk)  # <-- CAMBIADO
    except Alert.DoesNotExist:
        return Response({"error": "Alert not found"}, status=status.HTTP_404_NOT_FOUND)

    # GET: cualquiera autenticado
    if request.method == 'GET':
        serializer = AlertSerializer(alert)
        return Response(serializer.data)

    # PATCH / DELETE: solo dueño del nodo
    if alert.node.user_id != request.user.id:
        return Response(
            {"detail": "You do not own the node associated with this alert."},
            status=status.HTTP_403_FORBIDDEN
        )

    if request.method == 'PATCH':
        serializer = AlertSerializer(alert, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        # ELIMINAR: soft delete - usar eliminación física
        alert.delete()  # <-- CAMBIADO: eliminación física
        return Response(status=status.HTTP_204_NO_CONTENT)


# -----------------------------
# Alertas - Filtros avanzados
# -----------------------------

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def alert_filter(request):
    """
    Filter alerts by:
    - owner of the node
    - node
    - sensor
    - alert type (high / low)
    - status (pending / attended)
    - date range
    """
    alerts = Alert.objects.all()

    owner_id = request.query_params.get('owner_id')
    node_id = request.query_params.get('node_id')
    sensor_id = request.query_params.get('sensor_id')
    alert_type = request.query_params.get('alert_type')
    status_param = request.query_params.get('status')
    from_date = request.query_params.get('from_date')
    to_date = request.query_params.get('to_date')

    if owner_id:
        alerts = alerts.filter(node__user_id=owner_id)

    if node_id:
        alerts = alerts.filter(node_id=node_id)

    if sensor_id:
        alerts = alerts.filter(sensor_id=sensor_id)

    if alert_type in ('high', 'low'):
        alerts = alerts.filter(alert_type=alert_type)

    if status_param in ('pending', 'attended'):
        alerts = alerts.filter(status=status_param)

    if from_date:
        parsed_from = parse_datetime(from_date)
        if parsed_from:
            alerts = alerts.filter(created_at__gte=parsed_from)

    if to_date:
        parsed_to = parse_datetime(to_date)
        if parsed_to:
            alerts = alerts.filter(created_at__lte=parsed_to)

    serializer = AlertSerializer(alerts, many=True)
    return Response(serializer.data)