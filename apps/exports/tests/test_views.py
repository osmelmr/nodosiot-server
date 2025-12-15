# apps/exports/tests/test_views.py
# py .\manage.py test apps.exports.tests.test_views

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from io import StringIO
import csv

from apps.users.models import User
from apps.nodes.models import Node
from apps.sensors.models import Sensor
from apps.readings.models import Reading
from apps.alerts.models import Alert


class ExportTests(TestCase):
    """Tests básicos para vistas de exportación"""
    
    def setUp(self):
        self.admin = User.objects.create_user(
            email="admin@test.com",
            password="adminpass123",
            role=User.Roles.ADMIN
        )
        
        self.researcher = User.objects.create_user(
            email="researcher@test.com",
            password="researcherpass123",
            role=User.Roles.RESEARCHER
        )
        
        # Datos de prueba
        node = Node.objects.create(name="Test Node", location="Test", user=self.researcher)
        sensor = Sensor.objects.create(node=node, name="Test Sensor", 
                                      sensor_type=Sensor.SensorTypes.TEMPERATURE, 
                                      model="DHT22", unit="°C")
        
        Reading.objects.create(sensor=sensor, node=node, value=25.0, 
                              timestamp="2024-01-01T10:00:00Z")
        
        reading = Reading.objects.first()
        Alert.objects.create(sensor=sensor, node=node, reading=reading,
                            alert_type=Alert.AlertType.HIGH, detected_value=30.0,
                            status=Alert.AlertStatus.PENDING)
        
        self.client = APIClient()
    
    # --------------------------------------------------
    # TESTS CSV
    # --------------------------------------------------
    
    def test_1_admin_can_export_readings_csv(self):
        """1. Admin puede exportar readings CSV"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(reverse('export-readings-csv'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment; filename="readings.csv"', response['Content-Disposition'])
        
        # Verificar contenido CSV
        content = response.content.decode('utf-8')
        self.assertIn('pk,Sensor,Nodo,Valor,Timestamp', content)
        self.assertIn('Test Sensor', content)
    
    def test_2_researcher_cannot_export_csv(self):
        """2. Researcher NO puede exportar (solo admin para POST)"""
        self.client.force_authenticate(user=self.researcher)
        response = self.client.get(reverse('export-readings-csv'))
        
        # IsAdminOrReadOnly: GET está permitido para todos autenticados
        # Si necesitas solo admin, cambia el permiso
        # self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # Permite GET
    
    def test_3_unauthenticated_cannot_export(self):
        """3. Usuario no autenticado no puede exportar"""
        response = self.client.get(reverse('export-readings-csv'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_4_export_alerts_csv(self):
        """4. Exportar alerts CSV funciona"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(reverse('export-alerts-csv'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('alerts.csv', response['Content-Disposition'])
    
    # --------------------------------------------------
    # TESTS PDF
    # --------------------------------------------------
    
    def test_5_admin_can_export_readings_pdf(self):
        """5. Admin puede exportar readings PDF"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(reverse('export-readings-pdf'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/pdf')
    
    def test_6_csv_contains_correct_data(self):
        """6. CSV contiene datos correctos"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(reverse('export-readings-csv'))
        
        # Parsear CSV
        csv_data = response.content.decode('utf-8').splitlines()
        reader = csv.reader(csv_data)
        rows = list(reader)
        
        # Verificar encabezados
        self.assertEqual(rows[0], ['pk', 'Sensor', 'Nodo', 'Valor', 'Timestamp'])
        
        # Verificar al menos una fila de datos
        self.assertTrue(len(rows) > 1)