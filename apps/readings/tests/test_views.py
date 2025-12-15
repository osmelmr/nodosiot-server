# apps/readings/tests/test_views.py

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from apps.nodes.models import Node
from apps.sensors.models import Sensor
from apps.readings.models import Reading
from apps.alerts.models import Alert

User = get_user_model()


class ReadingViewTests(APITestCase):

    def setUp(self):
        # Usuario
        self.user = User.objects.create_user(
            email="user@test.com",
            password="user123",
            role="farmer",
        )

        # Nodo y sensor
        self.node = Node.objects.create(
            name="Node 1",
            description="Test node",
            sampling_interval=10,
            location="Test location",
        )

        self.sensor = Sensor.objects.create(
            node=self.node,
            name="Temperature Sensor",
            sensor_type="temperature",
            model="DHT22",
            unit="°C",
            min_value=0,
            max_value=50,
        )

        # Lectura inicial
        self.reading = Reading.objects.create(
            sensor=self.sensor,
            node=self.node,
            value=25,
            timestamp=timezone.now()
        )

        # URLs
        self.list_url = reverse("reading-list-create")
        self.detail_url = lambda r: reverse("reading-detail", kwargs={"pk": r.id})
        self.latest_url = reverse("reading-latest")

    # -----------------------------
    # AUTHENTICATION
    # -----------------------------
    def test_unauthenticated_user_cannot_access_list(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_user_cannot_create_reading(self):
        response = self.client.post(self.list_url, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # -----------------------------
    # LIST
    # -----------------------------
    def test_authenticated_user_can_list_readings(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_soft_deleted_reading_not_listed(self):
        self.client.force_authenticate(user=self.user)
        self.reading.is_deleted = True
        self.reading.save(update_fields=["is_deleted"])
        response = self.client.get(self.list_url)
        self.assertEqual(len(response.data), 0)

    # -----------------------------
    # CREATE
    # -----------------------------
    def test_authenticated_user_can_create_reading(self):
        self.client.force_authenticate(user=self.user)
        payload = {
            "sensor": self.sensor.id,
            "node": self.node.id,
            "value": 55,  # superará el max_value para generar alerta
            "timestamp": timezone.now(),
        }
        response = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Reading.objects.count(), 2)

        # Verificar alerta
        self.assertIn("alert", response.data)
        self.assertTrue(Alert.objects.filter(sensor=self.sensor).exists())

    def test_create_reading_invalid_payload(self):
        self.client.force_authenticate(user=self.user)
        payload = {"value": 20}  # falta sensor y node
        response = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # -----------------------------
    # DETAIL
    # -----------------------------
    def test_authenticated_user_can_retrieve_reading(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.detail_url(self.reading))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["value"], self.reading.value)

    def test_retrieve_soft_deleted_reading_returns_404(self):
        self.client.force_authenticate(user=self.user)
        self.reading.is_deleted = True
        self.reading.save(update_fields=["is_deleted"])
        response = self.client.get(self.detail_url(self.reading))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # -----------------------------
    # UPDATE
    # -----------------------------
    def test_authenticated_user_can_update_reading(self):
        self.client.force_authenticate(user=self.user)
        payload = {"value": 30}
        response = self.client.patch(self.detail_url(self.reading), payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.reading.refresh_from_db()
        self.assertEqual(self.reading.value, 30)

    # -----------------------------
    # DELETE
    # -----------------------------
    def test_authenticated_user_can_soft_delete_reading(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.detail_url(self.reading))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.reading.refresh_from_db()
        self.assertTrue(self.reading.is_deleted)

    def test_deleted_reading_not_retrievable(self):
        self.client.force_authenticate(user=self.user)
        self.reading.is_deleted = True
        self.reading.save(update_fields=["is_deleted"])
        response = self.client.get(self.detail_url(self.reading))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # -----------------------------
    # LATEST READINGS
    # -----------------------------
    def test_latest_readings_filter_by_interval(self):
        self.client.force_authenticate(user=self.user)
        # lectura vieja
        old_reading = Reading.objects.create(
            sensor=self.sensor,
            node=self.node,
            value=10,
            timestamp=timezone.now() - timedelta(minutes=120)
        )
        response = self.client.get(self.latest_url + "?interval=60")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # solo la lectura reciente
        self.assertNotIn(old_reading.id, [r["id"] for r in response.data])

    def test_latest_readings_filter_by_node_and_sensor(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(
            f"{self.latest_url}?node_id={self.node.id}&sensor_id={self.sensor.id}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
