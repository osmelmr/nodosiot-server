import csv
from io import StringIO, BytesIO
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from apps.readings.models import Reading
from apps.alerts.models import Alert
from apps.core.permissions import IsAdminOrReadOnly
from reportlab.pdfgen import canvas

# -----------------------------
# Export CSV
# -----------------------------

@api_view(['GET'])
@permission_classes([IsAdminOrReadOnly])
def export_readings_csv(request):
    readings = Reading.objects.filter(is_deleted=False)
    # opcional: filtrar por sensor, nodo, fechas
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['UUID', 'Sensor', 'Nodo', 'Valor', 'Timestamp'])
    for r in readings:
        writer.writerow([r.uuid, r.sensor.name, r.node.name, r.value, r.timestamp])
    response = HttpResponse(output.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="readings.csv"'
    return response


@api_view(['GET'])
@permission_classes([IsAdminOrReadOnly])
def export_alerts_csv(request):
    alerts = Alert.objects.filter(is_deleted=False)
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['UUID', 'Sensor', 'Nodo', 'Tipo alerta', 'Valor', 'Timestamp', 'Estado'])
    for a in alerts:
        writer.writerow([a.uuid, a.sensor.name, a.node.name, a.alert_type, a.detected_value, a.timestamp, a.status])
    response = HttpResponse(output.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="alerts.csv"'
    return response

# -----------------------------
# Export PDF (simple)
# -----------------------------

@api_view(['GET'])
@permission_classes([IsAdminOrReadOnly])
def export_readings_pdf(request):
    readings = Reading.objects.filter(is_deleted=False)
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    y = 800
    p.drawString(100, y, "Listado de Lecturas")
    y -= 30
    for r in readings:
        line = f"{r.uuid} | {r.sensor.name} | {r.node.name} | {r.value} | {r.timestamp}"
        p.drawString(50, y, line)
        y -= 20
        if y < 50:
            p.showPage()
            y = 800
    p.save()
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')
