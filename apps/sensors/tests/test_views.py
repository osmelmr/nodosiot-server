from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from apps.nodes.models import Node
from apps.sensors.models import Sensor

User = get_user_model()


class SensorViewTests(APITestCase):

    def setUp(self):
        # --------------------------------------------------
        # Usuarios
        # --------------------------------------------------
        self.user = User.objects.create_user(
            email="user@test.com",
            password="user123",
            role="farmer",
        )

        self.other_user = User.objects.create_user(
            email="other@test.com",
            password="other123",
            role="researcher",
        )

        # --------------------------------------------------
        # Nodo
        # --------------------------------------------------
        self.node = Node.objects.create(
            name="Node 1",
            description="Main node",
            sampling_interval=10,
            location="Field A",
        )

        # --------------------------------------------------
        # Sensores
        # --------------------------------------------------
        self.sensor_1 = Sensor.objects.create(
            node=self.node,
            name="Temperature Sensor",
            sensor_type="temperature",
            model="DHT22",
            unit="°C",
            min_value=0,
            max_value=50,
        )

        self.sensor_2 = Sensor.objects.create(
            node=self.node,
            name="Humidity Sensor",
            sensor_type="humidity",
            model="DHT22",
            unit="%",
        )

        # --------------------------------------------------
        # URLs
        # --------------------------------------------------
        self.sensor_list_url = reverse("sensor-list-create")
        self.sensor_detail_url = lambda s: reverse(
            "sensor-detail", kwargs={"pk": s.id}
        )

    # --------------------------------------------------
    # LIST
    # --------------------------------------------------

    def test_authenticated_user_can_list_sensors(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.sensor_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_unauthenticated_user_cannot_list_sensors(self):
        response = self.client.get(self.sensor_list_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --------------------------------------------------
    # CREATE
    # --------------------------------------------------

    def test_authenticated_user_can_create_sensor(self):
        self.client.force_authenticate(user=self.user)

        payload = {
            "node": self.node.id,
            "name": "Pressure Sensor",
            "sensor_type": "pressure",
            "model": "BMP280",
            "unit": "hPa",
            "min_value": 900,
            "max_value": 1100,
        }

        response = self.client.post(
            self.sensor_list_url, payload, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Sensor.objects.count(), 3)

    def test_cannot_create_sensor_without_authentication(self):
        payload = {
            "node": self.node.id,
            "name": "Fail Sensor",
            "sensor_type": "temperature",
            "model": "TMP36",
            "unit": "°C",
        }

        response = self.client.post(
            self.sensor_list_url, payload, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --------------------------------------------------
    # RETRIEVE
    # --------------------------------------------------

    def test_authenticated_user_can_retrieve_sensor(self):
        self.client.force_authenticate(user=self.other_user)

        response = self.client.get(
            self.sensor_detail_url(self.sensor_1)
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["name"],
            self.sensor_1.name
        )

    def test_retrieve_deleted_sensor_returns_404(self):
        self.client.force_authenticate(user=self.user)

        self.sensor_1.is_deleted = True
        self.sensor_1.save()

        response = self.client.get(
            self.sensor_detail_url(self.sensor_1)
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # --------------------------------------------------
    # UPDATE
    # --------------------------------------------------

    def test_authenticated_user_can_update_sensor(self):
        self.client.force_authenticate(user=self.user)

        payload = {
            "unit": "Celsius",
            "max_value": 60,
        }

        response = self.client.patch(
            self.sensor_detail_url(self.sensor_1),
            payload,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.sensor_1.refresh_from_db()
        self.assertEqual(self.sensor_1.unit, "Celsius")
        self.assertEqual(self.sensor_1.max_value, 60)

    def test_unauthenticated_user_cannot_update_sensor(self):
        response = self.client.patch(
            self.sensor_detail_url(self.sensor_1),
            {"unit": "Hack"},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --------------------------------------------------
    # DELETE (soft delete)
    # --------------------------------------------------

    def test_authenticated_user_can_soft_delete_sensor(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.delete(
            self.sensor_detail_url(self.sensor_1)
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.sensor_1.refresh_from_db()
        self.assertTrue(self.sensor_1.is_deleted)

    def test_unauthenticated_user_cannot_delete_sensor(self):
        response = self.client.delete(
            self.sensor_detail_url(self.sensor_1)
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
