from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from apps.nodes.models import Node

User = get_user_model()

class NodeViewsTests(APITestCase):
    def setUp(self):
        # -------------------------
        # Usuarios
        # -------------------------
        self.admin_user = User.objects.create_superuser(
            email="admin@test.com",
            password="adminpass"
        )
        self.normal_user = User.objects.create_user(
            email="user@test.com",
            password="userpass"
        )
        self.other_user = User.objects.create_user(
            email="other@test.com",
            password="otherpass"
        )

        # Nodo propiedad de normal_user (solo dueño, no admin)
        self.node = Node.objects.create(
            name="Node1",
            description="Test node",
            location="Lab",
            sampling_interval=15,
            user=self.normal_user
        )

        # Nodo propiedad de owner-admin (dueño y admin)
        self.owner_admin_user = User.objects.create_superuser(
            email="owneradmin@test.com",
            password="owneradminpass"
        )
        self.node_owner_admin = Node.objects.create(
            name="NodeOwnerAdmin",
            description="Node for owner-admin",
            location="Lab",
            sampling_interval=15,
            user=self.owner_admin_user
        )

        # -------------------------
        # URLs
        # -------------------------
        self.list_create_url = reverse('node-list-create')
        self.detail_url = lambda pk: reverse('node-detail', args=[pk])

    # -------------------------
    # Helper
    # -------------------------
    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    # -------------------------
    # GET /nodes/
    # -------------------------
    def test_any_authenticated_can_list_nodes(self):
        self.authenticate(self.normal_user)
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    # -------------------------
    # POST /nodes/
    # -------------------------
    def test_admin_can_create_node(self):
        self.authenticate(self.admin_user)
        payload = {
            "name": "NodeAdmin",
            "description": "Created by admin",
            "location": "Office",
            "sampling_interval": 20
        }
        response = self.client.post(self.list_create_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Node.objects.filter(name="NodeAdmin").exists())

    def test_non_admin_cannot_create_node(self):
        self.authenticate(self.normal_user)
        payload = {
            "name": "BlockedNode",
            "description": "Should fail",
            "location": "Office",
            "sampling_interval": 20
        }
        response = self.client.post(self.list_create_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # -------------------------
    # GET /nodes/<id>/
    # -------------------------
    def test_owner_can_retrieve_node(self):
        self.authenticate(self.normal_user)
        response = self.client.get(self.detail_url(self.node.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Node1")

    def test_other_user_can_retrieve_node(self):
        self.authenticate(self.other_user)
        response = self.client.get(self.detail_url(self.node.id))
        # Detalles debe ser publico tambien
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # -------------------------
    # PATCH /nodes/<id>/
    # -------------------------
    def test_other_user_cannot_update_node(self):
        self.authenticate(self.other_user)
        payload = {"name": "HackedName"}
        response = self.client.patch(self.detail_url(self.node.id), payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_admin_can_update_node(self):
        self.authenticate(self.owner_admin_user)
        payload = {"name": "UpdatedNode"}
        response = self.client.patch(self.detail_url(self.node_owner_admin.id), payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.node_owner_admin.refresh_from_db()
        self.assertEqual(self.node_owner_admin.name, "UpdatedNode")

    # -------------------------
    # DELETE /nodes/<id>/
    # -------------------------
    def test_owner_admin_can_delete_node(self):
        self.authenticate(self.owner_admin_user)
        response = self.client.delete(self.detail_url(self.node_owner_admin.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.node_owner_admin.refresh_from_db()
        self.assertTrue(self.node_owner_admin.is_deleted)

    def test_other_user_cannot_delete_node(self):
        self.authenticate(self.other_user)
        response = self.client.delete(self.detail_url(self.node.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.node.refresh_from_db()
        self.assertFalse(self.node.is_deleted)

    def test_admin_only_cannot_delete_node_if_not_owner(self):
        self.authenticate(self.admin_user)
        response = self.client.delete(self.detail_url(self.node.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.node.refresh_from_db()
        self.assertFalse(self.node.is_deleted)
