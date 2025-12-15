from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from apps.users.models import User
from apps.nodes.models import Node
from apps.sensors.models import Sensor

class SensorViewTests(APITestCase):

    def setUp(self):
        # -----------------------------
        # Usuarios
        # -----------------------------
        self.admin_user = User.objects.create_user(
            email="admin@test.com", password="admin123", role="admin"
        )
        self.owner_user = User.objects.create_user(
            email="owner@test.com", password="owner123", role="researcher"
        )
        self.other_user = User.objects.create_user(
            email="other@test.com", password="other123", role="researcher"
        )

        # -----------------------------
        # Nodo del propietario
        # -----------------------------
        self.node = Node.objects.create(
            name="Node 1",
            user=self.owner_user,  # Obligatorio
            location="Lab 1",
            sampling_interval=10
        )

        # -----------------------------
        # Sensor del nodo
        # -----------------------------
        self.sensor = Sensor.objects.create(
            node=self.node,
            name="Sensor 1",
            sensor_type="temperature",
            model="T1000",
            unit="C"
        )

    # -----------------------------
    # LIST / CREATE
    # -----------------------------
    def test_list_sensors_authenticated(self):
        self.client.force_login(self.owner_user)
        url = reverse('sensor-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_sensors_unauthenticated(self):
        url = reverse('sensor-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_sensor_admin(self):
        self.client.force_login(self.admin_user)
        url = reverse('sensor-list-create')
        data = {
            "node": self.node.id,
            "name": "Sensor 2",
            "sensor_type": "humidity",
            "model": "H2000",
            "unit": "%"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Sensor.objects.count(), 2)

    def test_create_sensor_non_admin(self):
        self.client.force_login(self.owner_user)
        url = reverse('sensor-list-create')
        data = {
            "node": self.node.id,
            "name": "Sensor 2",
            "sensor_type": "humidity",
            "model": "H2000",
            "unit": "%"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # -----------------------------
    # DETAIL / PATCH / DELETE
    # -----------------------------
    def test_get_sensor_detail_authenticated(self):
        self.client.force_login(self.other_user)
        url = reverse('sensor-detail', args=[self.sensor.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_sensor_detail_unauthenticated(self):
        url = reverse('sensor-detail', args=[self.sensor.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_sensor_owner(self):
        self.client.force_login(self.owner_user)
        url = reverse('sensor-detail', args=[self.sensor.id])
        response = self.client.patch(url, {"name": "Updated Sensor"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.sensor.refresh_from_db()
        self.assertEqual(self.sensor.name, "Updated Sensor")

    def test_patch_sensor_admin(self):
        self.client.force_login(self.admin_user)
        url = reverse('sensor-detail', args=[self.sensor.id])
        response = self.client.patch(url, {"name": "Admin Updated"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.sensor.refresh_from_db()
        self.assertEqual(self.sensor.name, "Admin Updated")

    def test_patch_sensor_other_user_forbidden(self):
        self.client.force_login(self.other_user)
        url = reverse('sensor-detail', args=[self.sensor.id])
        response = self.client.patch(url, {"name": "Fail Update"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_sensor_owner(self):
        self.client.force_login(self.owner_user)
        url = reverse('sensor-detail', args=[self.sensor.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.sensor.refresh_from_db()
        self.assertTrue(self.sensor.is_deleted)

    def test_delete_sensor_admin(self):
        self.client.force_login(self.admin_user)
        url = reverse('sensor-detail', args=[self.sensor.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.sensor.refresh_from_db()
        self.assertTrue(self.sensor.is_deleted)

    def test_delete_sensor_other_user_forbidden(self):
        self.client.force_login(self.other_user)
        url = reverse('sensor-detail', args=[self.sensor.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.sensor.refresh_from_db()
        self.assertFalse(self.sensor.is_deleted)
