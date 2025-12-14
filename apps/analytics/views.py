from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Avg, Max, Min
from apps.readings.models import Reading
from apps.core.permissions import IsAdminOrReadOnly
from datetime import datetime

# -----------------------------
# Métricas y agregaciones
# -----------------------------

@api_view(['GET'])
@permission_classes([IsAdminOrReadOnly])
def daily_summary(request):
    """
    Devuelve resumen diario por sensor y nodo.
    Query params:
      - node_id
      - sensor_id
      - start_date (YYYY-MM-DD)
      - end_date (YYYY-MM-DD)
    """
    node_id = request.query_params.get('node_id')
    sensor_id = request.query_params.get('sensor_id')
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')

    readings = Reading.objects.filter(is_deleted=False)

    if node_id:
        readings = readings.filter(node_id=node_id)
    if sensor_id:
        readings = readings.filter(sensor_id=sensor_id)
    if start_date:
        readings = readings.filter(timestamp__gte=start_date)
    if end_date:
        readings = readings.filter(timestamp__lte=end_date)

    summary = readings.aggregate(
        avg_value=Avg('value'),
        max_value=Max('value'),
        min_value=Min('value')
    )

    return Response(summary)
