from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class UserViewsTests(APITestCase):
    def setUp(self):
        # Creamos un usuario admin
        self.admin_user = User.objects.create_superuser(
            email="admin@test.com",
            password="adminpass"
        )

        # Creamos un usuario normal
        self.normal_user = User.objects.create_user(
            email="user@test.com",
            password="userpass"
        )

        # Endpoints
        self.list_create_url = reverse('user_list_create')  # define tu path name
        self.login_url = reverse('user_login')

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    # -------------------------
    # Tests GET /users/
    # -------------------------
    def test_admin_can_list_users(self):
        self.authenticate(self.admin_user)
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 2)

    def test_non_admin_cannot_list_users(self):
        self.authenticate(self.normal_user)
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # -------------------------
    # Tests POST /users/
    # -------------------------
    def test_admin_can_create_user(self):
        self.authenticate(self.admin_user)
        payload = {
            "email": "newuser@test.com",
            "password": "newpass123",
            "role": "researcher"
        }
        response = self.client.post(self.list_create_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="newuser@test.com").exists())

    def test_non_admin_cannot_create_user(self):
        self.authenticate(self.normal_user)
        payload = {
            "email": "blocked@test.com",
            "password": "pass123"
        }
        response = self.client.post(self.list_create_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # -------------------------
    # Tests PATCH /users/<id>/
    # -------------------------
    def test_admin_can_update_user(self):
        self.authenticate(self.admin_user)
        url = reverse('user_detail', args=[self.normal_user.id])
        payload = {"role": "admin", "password": "newpass456"}
        response = self.client.patch(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.normal_user.refresh_from_db()
        self.assertEqual(self.normal_user.role, "admin")
        self.assertTrue(self.normal_user.check_password("newpass456"))

    # -------------------------
    # Tests DELETE /users/<id>/
    # -------------------------
    def test_admin_can_delete_user(self):
        self.authenticate(self.admin_user)
        url = reverse('user_detail', args=[self.normal_user.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(id=self.normal_user.id).exists())

    # -------------------------
    # Tests POST /login/
    # -------------------------
    def test_login_success(self):
        payload = {"email": "admin@test.com", "password": "adminpass"}
        response = self.client.post(self.login_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_fail_invalid_credentials(self):
        payload = {"email": "admin@test.com", "password": "wrongpass"}
        response = self.client.post(self.login_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
