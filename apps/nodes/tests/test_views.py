from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from apps.nodes.models import Node

User = get_user_model()


class NodeViewTests(APITestCase):

    def setUp(self):
        # ----- Usuarios -----
        self.admin_user = User.objects.create_user(
            email="admin@test.com",
            password="admin123",
            role="admin",
            is_staff=True,
            is_superuser=True,
        )

        self.normal_user = User.objects.create_user(
            email="user@test.com",
            password="user123",
            role="farmer",
        )

        # ----- Nodos -----
        self.node_1 = Node.objects.create(
            name="Node 1",
            description="Main node",
            sampling_interval=10,
            location="Field A",
            latitude=10.123456,
            longitude=-70.654321,
        )

        self.node_2 = Node.objects.create(
            name="Node 2",
            description="Backup node",
            sampling_interval=20,
            location="Field B",
        )

        # ----- URLs -----
        self.node_list_url = reverse("node-list-create")
        self.node_detail_url = lambda n: reverse(
            "node-detail", kwargs={"pk": n.id}
        )

    # --------------------------------------------------
    # LIST
    # --------------------------------------------------

    def test_authenticated_user_can_list_nodes(self):
        self.client.force_authenticate(user=self.normal_user)

        response = self.client.get(self.node_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_unauthenticated_user_cannot_list_nodes(self):
        response = self.client.get(self.node_list_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --------------------------------------------------
    # CREATE
    # --------------------------------------------------

    def test_admin_can_create_node(self):
        self.client.force_authenticate(user=self.admin_user)

        payload = {
            "name": "New Node",
            "description": "New deployment",
            "sampling_interval": 15,
            "location": "Field C",
            "latitude": 12.345678,
            "longitude": -71.987654,
        }

        response = self.client.post(
            self.node_list_url, payload, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Node.objects.count(), 3)

    def test_non_admin_cannot_create_node(self):
        self.client.force_authenticate(user=self.normal_user)

        payload = {
            "name": "Fail Node",
            "sampling_interval": 10,
            "location": "Nowhere",
        }

        response = self.client.post(
            self.node_list_url, payload, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # --------------------------------------------------
    # RETRIEVE
    # --------------------------------------------------

    def test_authenticated_user_can_retrieve_node(self):
        self.client.force_authenticate(user=self.normal_user)

        response = self.client.get(
            self.node_detail_url(self.node_1)
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.node_1.name)

    def test_retrieve_deleted_node_returns_404(self):
        self.client.force_authenticate(user=self.admin_user)

        self.node_1.is_deleted = True
        self.node_1.save()

        response = self.client.get(
            self.node_detail_url(self.node_1)
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # --------------------------------------------------
    # UPDATE
    # --------------------------------------------------

    def test_admin_can_update_node(self):
        self.client.force_authenticate(user=self.admin_user)

        payload = {
            "sampling_interval": 30,
            "location": "Updated Field"
        }

        response = self.client.patch(
            self.node_detail_url(self.node_1),
            payload,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.node_1.refresh_from_db()
        self.assertEqual(self.node_1.sampling_interval, 30)
        self.assertEqual(self.node_1.location, "Updated Field")

    def test_non_admin_cannot_update_node(self):
        self.client.force_authenticate(user=self.normal_user)

        response = self.client.patch(
            self.node_detail_url(self.node_1),
            {"location": "Hack attempt"},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # --------------------------------------------------
    # DELETE (soft delete)
    # --------------------------------------------------

    def test_admin_can_soft_delete_node(self):
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.delete(
            self.node_detail_url(self.node_1)
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.node_1.refresh_from_db()
        self.assertTrue(self.node_1.is_deleted)

    def test_non_admin_cannot_delete_node(self):
        self.client.force_authenticate(user=self.normal_user)

        response = self.client.delete(
            self.node_detail_url(self.node_1)
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
