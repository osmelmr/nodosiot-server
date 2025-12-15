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
    # CORREGIDO: Eliminar .filter(is_deleted=False) - Reading no tiene ese campo
    readings = Reading.objects.all()  # <-- CAMBIADO
    
    # opcional: filtrar por sensor, nodo, fechas
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['pk', 'Sensor', 'Nodo', 'Valor', 'Timestamp'])
    for r in readings:
        writer.writerow([r.pk, r.sensor.name, r.node.name, r.value, r.timestamp])
    response = HttpResponse(output.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="readings.csv"'
    return response


@api_view(['GET'])
@permission_classes([IsAdminOrReadOnly])
def export_alerts_csv(request):
    # CORREGIDO: Eliminar .filter(is_deleted=False) - Alert no tiene ese campo
    alerts = Alert.objects.all()  # <-- CAMBIADO
    
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['pk', 'Sensor', 'Nodo', 'Tipo alerta', 'Valor', 'Timestamp', 'Estado'])
    
    # CORREGIDO: Alert tiene 'detected_value', no 'timestamp'. Usar 'created_at' en su lugar
    for a in alerts:
        writer.writerow([
            a.pk, 
            a.sensor.name, 
            a.node.name, 
            a.alert_type, 
            a.detected_value, 
            a.created_at,  # <-- CAMBIADO: Alert no tiene timestamp, usar created_at
            a.status
        ])
    
    response = HttpResponse(output.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="alerts.csv"'
    return response

# -----------------------------
# Export PDF (simple)
# -----------------------------

@api_view(['GET'])
@permission_classes([IsAdminOrReadOnly])
def export_readings_pdf(request):
    # CORREGIDO: Eliminar .filter(is_deleted=False)
    readings = Reading.objects.all()  # <-- CAMBIADO
    
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    y = 800
    p.drawString(100, y, "Listado de Lecturas")
    y -= 30
    for r in readings:
        line = f"{r.pk} | {r.sensor.name} | {r.node.name} | {r.value} | {r.timestamp}"
        p.drawString(50, y, line)
        y -= 20
        if y < 50:
            p.showPage()
            y = 800
    p.save()
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')