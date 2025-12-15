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
        self.admin_user = User.objects.create_user(
            email="admin@test.com", password="admin123", role="admin"
        )
        self.owner_user = User.objects.create_user(
            email="owner@test.com", password="owner123", role="researcher"
        )
        self.other_user = User.objects.create_user(
            email="other@test.com", password="other123", role="researcher"
        )

        # --------------------------------------------------
        # Nodo
        # --------------------------------------------------
        self.node = Node.objects.create(
            name="Node 1",
            description="Main node",
            sampling_interval=10,
            location="Field A",
            user=self.owner_user
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
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(self.sensor_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_unauthenticated_user_cannot_list_sensors(self):
        response = self.client.get(self.sensor_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --------------------------------------------------
    # CREATE
    # --------------------------------------------------
    def test_owner_and_admin_can_create_sensor(self):
        # Solo combinación owner + admin debería permitir creación
        self.client.force_authenticate(user=self.owner_user)
        payload = {
            "node": self.node.id,
            "name": "Pressure Sensor",
            "sensor_type": "pressure",
            "model": "BMP280",
            "unit": "hPa",
        }
        response = self.client.post(self.sensor_list_url, payload, format="json")
        # En este caso owner solo no crea: 403
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Ahora admin + owner (simulando que admin es dueño del nodo)
        self.node.user = self.admin_user
        self.node.save()
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(self.sensor_list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_other_user_cannot_create_sensor(self):
        self.client.force_authenticate(user=self.other_user)
        payload = {
            "node": self.node.id,
            "name": "Fail Sensor",
            "sensor_type": "temperature",
            "model": "TMP36",
            "unit": "°C",
        }
        response = self.client.post(self.sensor_list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # --------------------------------------------------
    # RETRIEVE
    # --------------------------------------------------
    def test_authenticated_user_can_retrieve_sensor(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(self.sensor_detail_url(self.sensor_1))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.sensor_1.name)

    # --------------------------------------------------
    # UPDATE
    # --------------------------------------------------
    def test_admin_and_owner_can_update_sensor(self):
        # No cumple ambas condiciones → 403
        self.client.force_authenticate(user=self.owner_user)
        payload = {"unit": "Celsius"}
        response = self.client.patch(self.sensor_detail_url(self.sensor_1), payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Ahora cumple ambas condiciones
        self.node.user = self.admin_user
        self.node.save()
        self.client.force_authenticate(user=self.admin_user)
        payload = {"unit": "Fahrenheit"}
        response = self.client.patch(self.sensor_detail_url(self.sensor_1), payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.sensor_1.refresh_from_db()
        self.assertEqual(self.sensor_1.unit, "Fahrenheit")

    def test_other_user_cannot_update_sensor(self):
        self.client.force_authenticate(user=self.other_user)
        payload = {"unit": "Hack"}
        response = self.client.patch(self.sensor_detail_url(self.sensor_1), payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # --------------------------------------------------
    # DELETE (soft delete)
    # --------------------------------------------------
    def test_admin_and_owner_can_soft_delete_sensor(self):
        # No cumple ambas condiciones → 403
        self.client.force_authenticate(user=self.owner_user)
        response = self.client.delete(self.sensor_detail_url(self.sensor_1))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Cumple ambas condiciones
        self.node.user = self.admin_user
        self.node.save()
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.sensor_detail_url(self.sensor_1))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.sensor_1.refresh_from_db()
        self.assertTrue(self.sensor_1.is_deleted)

    def test_other_user_cannot_delete_sensor(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(self.sensor_detail_url(self.sensor_2))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.sensor_2.refresh_from_db()
        self.assertFalse(self.sensor_2.is_deleted)
