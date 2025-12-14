from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Alert
from .serializers import AlertSerializer
from apps.core.permissions import IsAdminOrReadOnly

# -----------------------------
# Alertas
# -----------------------------

@api_view(['GET', 'POST'])
@permission_classes([IsAdminOrReadOnly])
def alert_list_create(request):
    """
    List all alerts or create a new alert.
    """
    if request.method == 'GET':
        alerts = Alert.objects.filter(is_deleted=False)
        serializer = AlertSerializer(alerts, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = AlertSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAdminOrReadOnly])
def alert_detail(request, uuid):
    """
    Retrieve, update, or delete an alert by UUID.
    """
    try:
        alert = Alert.objects.get(uuid=uuid, is_deleted=False)
    except Alert.DoesNotExist:
        return Response({"error": "Alert not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = AlertSerializer(alert)
        return Response(serializer.data)

    if request.method == 'PATCH':
        serializer = AlertSerializer(alert, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        alert.is_deleted = True
        alert.save(update_fields=['is_deleted'])
        return Response(status=status.HTTP_204_NO_CONTENT)
