# apps/analytics/tests/test_views.py
# py .\manage.py test apps.analytics.tests.test_views

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone
from datetime import datetime, timedelta

from apps.users.models import User
from apps.nodes.models import Node
from apps.sensors.models import Sensor
from apps.readings.models import Reading


class DailySummaryTests(TestCase):
    """Tests para la vista daily_summary"""
    
    def setUp(self):
        # Usuarios
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
        
        # Nodo
        self.node = Node.objects.create(
            name="Test Node",
            location="Test Location",
            user=self.researcher
        )
        
        # Sensor
        self.sensor = Sensor.objects.create(
            node=self.node,
            name="Temperature Sensor",
            sensor_type=Sensor.SensorTypes.TEMPERATURE,
            model="DHT22",
            unit="°C"
        )
        
        # Crear lecturas con diferentes valores y fechas
        now = timezone.now()
        
        # Lecturas para hoy
        self.reading1 = Reading.objects.create(
            sensor=self.sensor,
            node=self.node,
            value=20.0,
            timestamp=now - timedelta(hours=2)
        )
        
        self.reading2 = Reading.objects.create(
            sensor=self.sensor,
            node=self.node,
            value=25.0,
            timestamp=now - timedelta(hours=1)
        )
        
        self.reading3 = Reading.objects.create(
            sensor=self.sensor,
            node=self.node,
            value=30.0,
            timestamp=now
        )
        
        # Lectura antigua (no debería incluirse en filtro por fecha)
        self.old_reading = Reading.objects.create(
            sensor=self.sensor,
            node=self.node,
            value=15.0,
            timestamp=now - timedelta(days=10)
        )
        
        # URL - Asegúrate de que este nombre coincide con tus URLs
        # Si no se llama 'daily-summary', cámbialo
        self.daily_summary_url = reverse('daily-summary')
        
        # Cliente API
        self.client = APIClient()
    
    def test_1_unauthenticated_user_cannot_access(self):
        """1. Usuario no autenticado no puede acceder"""
        response = self.client.get(self.daily_summary_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_2_researcher_can_access_summary(self):
        """2. Researcher puede acceder al resumen"""
        self.client.force_authenticate(user=self.researcher)
        
        response = self.client.get(self.daily_summary_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que contiene las métricas
        self.assertIn('avg_value', response.data)
        self.assertIn('max_value', response.data)
        self.assertIn('min_value', response.data)
        
        # Cálculos para todas las lecturas: (20+25+30+15)/4 = 22.5
        self.assertEqual(float(response.data['avg_value']), 22.5)
        self.assertEqual(float(response.data['max_value']), 30.0)
        self.assertEqual(float(response.data['min_value']), 15.0)
    
    def test_3_admin_can_access_summary(self):
        """3. Admin puede acceder al resumen"""
        self.client.force_authenticate(user=self.admin)
        
        response = self.client.get(self.daily_summary_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Mismos cálculos que researcher
        self.assertEqual(float(response.data['avg_value']), 22.5)
        self.assertEqual(float(response.data['max_value']), 30.0)
        self.assertEqual(float(response.data['min_value']), 15.0)
    
    def test_4_filter_by_node(self):
        """4. Filtrar resumen por nodo específico"""
        self.client.force_authenticate(user=self.researcher)
        
        # Crear otro nodo con una lectura
        node2 = Node.objects.create(
            name="Other Node",
            location="Other Location",
            user=self.researcher
        )
        
        sensor2 = Sensor.objects.create(
            node=node2,
            name="Other Sensor",
            sensor_type=Sensor.SensorTypes.HUMIDITY,
            model="DHT22",
            unit="%"
        )
        
        # Crear lectura con valor diferente
        Reading.objects.create(
            sensor=sensor2,
            node=node2,
            value=100.0,
            timestamp=timezone.now()
        )
        
        # Filtrar solo por node2
        params = {'node_id': node2.id}
        response = self.client.get(self.daily_summary_url, params)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Solo la lectura del node2 (valor 100)
        self.assertEqual(float(response.data['avg_value']), 100.0)
        self.assertEqual(float(response.data['max_value']), 100.0)
        self.assertEqual(float(response.data['min_value']), 100.0)
    
    def test_5_filter_by_sensor(self):
        """5. Filtrar resumen por sensor específico"""
        self.client.force_authenticate(user=self.researcher)
        
        # Crear otro sensor en el mismo nodo
        sensor2 = Sensor.objects.create(
            node=self.node,
            name="Humidity Sensor",
            sensor_type=Sensor.SensorTypes.HUMIDITY,
            model="DHT22",
            unit="%"
        )
        
        # Crear lectura con el segundo sensor
        Reading.objects.create(
            sensor=sensor2,
            node=self.node,
            value=80.0,
            timestamp=timezone.now()
        )
        
        # Filtrar solo por sensor original
        params = {'sensor_id': self.sensor.id}
        response = self.client.get(self.daily_summary_url, params)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Solo las 4 lecturas del sensor original (20, 25, 30, 15)
        self.assertEqual(float(response.data['avg_value']), 22.5)
        self.assertEqual(float(response.data['max_value']), 30.0)
        self.assertEqual(float(response.data['min_value']), 15.0)
    
    def test_6_empty_result_with_filters(self):
        """6. Resultado vacío cuando filtros no coinciden"""
        self.client.force_authenticate(user=self.researcher)
        
        # Filtrar por ID inexistente
        params = {'node_id': 999}
        response = self.client.get(self.daily_summary_url, params)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Debe retornar None en todas las métricas cuando no hay resultados
        self.assertIsNone(response.data['avg_value'])
        self.assertIsNone(response.data['max_value'])
        self.assertIsNone(response.data['min_value'])