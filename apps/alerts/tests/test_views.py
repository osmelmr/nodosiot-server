# apps/alerts/tests/test_views.py
# py .\manage.py test apps.alerts.tests.test_views

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone
from datetime import timedelta

from apps.users.models import User
from apps.nodes.models import Node
from apps.sensors.models import Sensor
from apps.readings.models import Reading
from apps.alerts.models import Alert


class AlertEssentialTests(TestCase):
    """Los 10 tests más fundamentales para las vistas de alerts"""
    
    def setUp(self):
        # Usuarios básicos
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
        
        self.researcher2 = User.objects.create_user(
            email="researcher2@test.com",
            password="researcher2pass123",
            role=User.Roles.RESEARCHER
        )
        
        # Nodos
        self.node1 = Node.objects.create(
            name="Test Node 1",
            location="Test Location 1",
            user=self.researcher
        )
        
        self.node2 = Node.objects.create(
            name="Test Node 2",
            location="Test Location 2",
            user=self.researcher2
        )
        
        # Sensores
        self.sensor1 = Sensor.objects.create(
            node=self.node1,
            name="Temperature Sensor",
            sensor_type=Sensor.SensorTypes.TEMPERATURE,
            model="DHT22",
            unit="°C"
        )
        
        self.sensor2 = Sensor.objects.create(
            node=self.node2,
            name="Humidity Sensor",
            sensor_type=Sensor.SensorTypes.HUMIDITY,
            model="DHT22",
            unit="%"
        )
        
        # Lecturas
        self.reading1 = Reading.objects.create(
            sensor=self.sensor1,
            node=self.node1,
            value=50.0,
            timestamp=timezone.now(),
            validation_status=Reading.ValidationStatus.HIGH
        )
        
        self.reading2 = Reading.objects.create(
            sensor=self.sensor2,
            node=self.node2,
            value=10.0,
            timestamp=timezone.now(),
            validation_status=Reading.ValidationStatus.LOW
        )
        
        # Alertas
        self.alert1 = Alert.objects.create(
            sensor=self.sensor1,
            node=self.node1,
            reading=self.reading1,
            alert_type=Alert.AlertType.HIGH,
            detected_value=50.0,
            status=Alert.AlertStatus.PENDING
        )
        
        self.alert2 = Alert.objects.create(
            sensor=self.sensor2,
            node=self.node2,
            reading=self.reading2,
            alert_type=Alert.AlertType.LOW,
            detected_value=10.0,
            status=Alert.AlertStatus.ATTENDED
        )
        
        # URLs
        self.list_url = reverse('alert-list-create')
        self.filter_url = reverse('alert-filter')
        
        # Cliente API
        self.client = APIClient()
    
    def get_detail_url(self, alert_id):
        """Helper para obtener URL de detalle"""
        return reverse('alert-detail', kwargs={'pk': alert_id})
    
    # ------------------------------------------------------------
    # TESTS BÁSICOS DE AUTENTICACIÓN Y PERMISOS
    # ------------------------------------------------------------
    
    def test_1_unauthenticated_user_cannot_access_alerts(self):
        """1. Usuario no autenticado no puede acceder a alertas"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        detail_url = self.get_detail_url(self.alert1.id)
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_2_authenticated_user_can_list_alerts(self):
        """2. Usuario autenticado puede listar alertas (GET)"""
        self.client.force_authenticate(user=self.researcher)
        
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Ambas alertas
    
    def test_3_researcher_can_create_alert(self):
        """3. Researcher puede crear alertas (POST)"""
        self.client.force_authenticate(user=self.researcher)
        
        data = {
            "sensor": self.sensor1.id,
            "node": self.node1.id,
            "reading": self.reading1.id,
            "alert_type": Alert.AlertType.HIGH,
            "detected_value": 60.0,
            "status": Alert.AlertStatus.PENDING
        }
        
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Alert.objects.count(), 3)
        self.assertEqual(response.data['alert_type'], 'high')
        self.assertEqual(response.data['detected_value'], 60.0)
    
    # ------------------------------------------------------------
    # TESTS DE DETALLE (GET, PATCH, DELETE)
    # ------------------------------------------------------------
    
    def test_4_any_user_can_view_any_alert_detail(self):
        """4. Cualquier usuario autenticado puede ver detalle de cualquier alerta (GET)"""
        self.client.force_authenticate(user=self.researcher)
        
        # Researcher puede ver alerta de researcher2
        url = self.get_detail_url(self.alert2.id)
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.alert2.id)
        self.assertEqual(response.data['alert_type'], 'low')
    
    def test_5_owner_can_update_own_alert(self):
        """5. Dueño del nodo puede actualizar su alerta (PATCH)"""
        self.client.force_authenticate(user=self.researcher)
        
        url = self.get_detail_url(self.alert1.id)
        data = {"status": Alert.AlertStatus.ATTENDED}
        
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que se actualizó
        self.alert1.refresh_from_db()
        self.assertEqual(self.alert1.status, Alert.AlertStatus.ATTENDED)
        self.assertEqual(response.data['status'], 'attended')
    
    def test_6_non_owner_cannot_update_alert(self):
        """6. Usuario NO dueño NO puede actualizar alerta (PATCH)"""
        self.client.force_authenticate(user=self.researcher)
        
        # Researcher intenta actualizar alerta de researcher2
        url = self.get_detail_url(self.alert2.id)
        data = {"status": Alert.AlertStatus.PENDING}
        
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('detail', response.data)
        
        # Verificar que NO se actualizó
        self.alert2.refresh_from_db()
        self.assertEqual(self.alert2.status, Alert.AlertStatus.ATTENDED)  # Sigue igual
    
    def test_7_owner_can_delete_own_alert(self):
        """7. Dueño puede eliminar su alerta (DELETE físico)"""
        self.client.force_authenticate(user=self.researcher)
        
        url = self.get_detail_url(self.alert1.id)
        initial_count = Alert.objects.count()
        
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verificar que se eliminó físicamente
        self.assertEqual(Alert.objects.count(), initial_count - 1)
        
        # Verificar que no existe más
        with self.assertRaises(Alert.DoesNotExist):
            Alert.objects.get(id=self.alert1.id)
    
    def test_8_non_owner_cannot_delete_alert(self):
        """8. Usuario NO dueño NO puede eliminar alerta"""
        self.client.force_authenticate(user=self.researcher)
        
        url = self.get_detail_url(self.alert2.id)
        initial_count = Alert.objects.count()
        
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Verificar que NO se eliminó
        self.assertEqual(Alert.objects.count(), initial_count)
        # Verificar que todavía existe
        self.assertTrue(Alert.objects.filter(id=self.alert2.id).exists())
    
    # ------------------------------------------------------------
    # TESTS DE FILTROS
    # ------------------------------------------------------------
    
    def test_9_filter_alerts_by_node(self):
        """9. Filtrar alertas por nodo específico"""
        self.client.force_authenticate(user=self.researcher)
        
        # Filtrar por node1
        params = {'node_id': self.node1.id}
        response = self.client.get(self.filter_url, params)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['node'], self.node1.id)
        self.assertEqual(response.data[0]['alert_type'], 'high')
    
    def test_10_filter_alerts_multiple_criteria(self):
        """10. Filtrar alertas con múltiples criterios"""
        self.client.force_authenticate(user=self.researcher)
        
        # Crear más alertas para mejor testing
        alert3 = Alert.objects.create(
            sensor=self.sensor1,
            node=self.node1,
            reading=self.reading1,
            alert_type=Alert.AlertType.HIGH,
            detected_value=55.0,
            status=Alert.AlertStatus.PENDING
        )
        
        # Filtrar: alertas HIGH y PENDING del node1
        params = {
            'node_id': self.node1.id,
            'alert_type': 'high',
            'status': 'pending'
        }
        
        response = self.client.get(self.filter_url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Debería encontrar 2 alertas (alert1 y alert3)
        self.assertEqual(len(response.data), 2)
        
        # Verificar que cumplen todos los criterios
        for alert_data in response.data:
            self.assertEqual(alert_data['node'], self.node1.id)
            self.assertEqual(alert_data['alert_type'], 'high')
            self.assertEqual(alert_data['status'], 'pending')