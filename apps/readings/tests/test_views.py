# apps/readings/tests/test_views.py
# py .\manage.py test apps.readings.tests.test_views

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


class ReadingEssentialTests(TestCase):
    """Los 10 tests más fundamentales para las vistas de readings"""
    
    def setUp(self):
        # Usuarios básicos
        self.admin = User.objects.create_user(
            email="admin@test.com",
            password="adminpass",
            role=User.Roles.ADMIN
        )
        
        self.researcher = User.objects.create_user(
            email="researcher@test.com",
            password="researcherpass",
            role=User.Roles.RESEARCHER
        )
        
        # Nodo del researcher
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
        
        # URLs
        self.list_url = reverse('reading-list-create')
        self.latest_url = reverse('reading-latest')
        
        # Cliente API
        self.client = APIClient()
    
    def test_1_unauthenticated_user_cannot_access(self):
        """1. Usuario no autenticado no puede acceder a las vistas"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        response = self.client.post(self.list_url, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_2_researcher_can_list_readings(self):
        """2. Researcher autenticado puede listar readings (GET)"""
        self.client.force_authenticate(user=self.researcher)
        
        # Crear una lectura de ejemplo
        Reading.objects.create(
            sensor=self.sensor,
            node=self.node,
            value=25.0,
            timestamp=timezone.now(),
            validation_status=Reading.ValidationStatus.VALID
        )
        
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_3_researcher_cannot_create_reading(self):
        """3. Researcher NO puede crear reading (POST) - solo admin"""
        self.client.force_authenticate(user=self.researcher)
        
        data = {
            "sensor": self.sensor.id,
            "node": self.node.id,
            "value": 25.5,
            "timestamp": timezone.now().isoformat(),
            "validation_status": Reading.ValidationStatus.VALID
        }
        
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_4_admin_can_create_reading(self):
        """4. Admin puede crear reading (POST)"""
        self.client.force_authenticate(user=self.admin)
        
        data = {
            "sensor": self.sensor.id,
            "node": self.node.id,
            "value": 25.5,
            "timestamp": timezone.now().isoformat(),
            "validation_status": Reading.ValidationStatus.VALID
        }
        
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Reading.objects.count(), 1)
    
    def test_5_create_reading_with_high_alert(self):
        """5. Al crear reading con status HIGH, se genera alerta automáticamente"""
        self.client.force_authenticate(user=self.admin)
        
        data = {
            "sensor": self.sensor.id,
            "node": self.node.id,
            "value": 50.0,
            "timestamp": timezone.now().isoformat(),
            "validation_status": Reading.ValidationStatus.HIGH
        }
        
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verificar que se creó la alerta
        self.assertEqual(Alert.objects.count(), 1)
        alert = Alert.objects.first()
        self.assertEqual(alert.alert_type, 'high')
        
        # Verificar que la respuesta incluye la alerta
        self.assertIn('alert', response.data)
    
    def test_6_retrieve_single_reading(self):
        """6. Obtener una lectura específica por ID"""
        # Crear una lectura
        reading = Reading.objects.create(
            sensor=self.sensor,
            node=self.node,
            value=25.0,
            timestamp=timezone.now(),
            validation_status=Reading.ValidationStatus.VALID
        )
        
        self.client.force_authenticate(user=self.researcher)
        url = reverse('reading-detail', kwargs={'pk': reading.id})
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], reading.id)
        self.assertEqual(response.data['value'], 25.0)
    
    def test_7_admin_can_update_own_node_reading(self):
        """7. Admin puede actualizar reading de un nodo que le pertenece"""
        # Cambiar el dueño del nodo a admin
        self.node.user = self.admin
        self.node.save()
        
        # Crear una lectura
        reading = Reading.objects.create(
            sensor=self.sensor,
            node=self.node,
            value=25.0,
            timestamp=timezone.now(),
            validation_status=Reading.ValidationStatus.VALID
        )
        
        self.client.force_authenticate(user=self.admin)
        url = reverse('reading-detail', kwargs={'pk': reading.id})
        
        data = {"value": 30.0}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        reading.refresh_from_db()
        self.assertEqual(reading.value, 30.0)
    
    def test_8_admin_cannot_update_other_user_node_reading(self):
        """8. Admin NO puede actualizar reading de un nodo que no es suyo"""
        # El nodo pertenece al researcher, no al admin
        reading = Reading.objects.create(
            sensor=self.sensor,
            node=self.node,
            value=25.0,
            timestamp=timezone.now(),
            validation_status=Reading.ValidationStatus.VALID
        )
        
        self.client.force_authenticate(user=self.admin)
        url = reverse('reading-detail', kwargs={'pk': reading.id})
        
        data = {"value": 30.0}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        reading.refresh_from_db()
        self.assertEqual(reading.value, 25.0)  # No cambió
    
    def test_9_latest_readings_with_time_filter(self):
        """9. Latest readings puede filtrarse por intervalo de tiempo"""
        self.client.force_authenticate(user=self.researcher)
        
        # Crear lecturas con diferentes timestamps
        now = timezone.now()
        recent = now - timedelta(minutes=2)
        old = now - timedelta(minutes=10)
        
        reading1 = Reading.objects.create(
            sensor=self.sensor,
            node=self.node,
            value=25.0,
            timestamp=recent,
            validation_status=Reading.ValidationStatus.VALID
        )
        
        Reading.objects.create(
            sensor=self.sensor,
            node=self.node,
            value=20.0,
            timestamp=old,
            validation_status=Reading.ValidationStatus.VALID
        )
        
        # Filtrar últimos 5 minutos
        response = self.client.get(self.latest_url, {'interval': 5, 'unit': 'minutes'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Solo la reciente
        self.assertEqual(response.data[0]['id'], reading1.id)
    
    def test_10_admin_can_delete_own_node_reading(self):
        """10. Admin puede eliminar reading de un nodo que le pertenece"""
        # Cambiar el dueño del nodo a admin
        self.node.user = self.admin
        self.node.save()
        
        reading = Reading.objects.create(
            sensor=self.sensor,
            node=self.node,
            value=25.0,
            timestamp=timezone.now(),
            validation_status=Reading.ValidationStatus.VALID
        )
        
        self.client.force_authenticate(user=self.admin)
        url = reverse('reading-detail', kwargs={'pk': reading.id})
        
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Reading.objects.count(), 0)