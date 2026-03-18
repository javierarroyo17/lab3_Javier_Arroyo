from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


class SignupEndpointTests(APITestCase):
    def test_signup_returns_400_when_first_name_and_last_name_are_missing(self):
        payload = {
            "username": "newuser",
            "password": "strongpass123",
            "email": "newuser@example.com",
        }

        response = self.client.post(reverse("user-signup"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("first_name", response.data)
        self.assertIn("last_name", response.data)
        self.assertFalse(User.objects.filter(username=payload["username"]).exists())

    def test_signup_create_successfully_with_first_name_and_last_name(self):
        payload = {
            "username": "newuser",
            "password": "strongpass123",
            "first_name": "New",
            "last_name": "User",
            "email": "newuser@example.com",
        }

        response = self.client.post(reverse("user-signup"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["username"], payload["username"])
        self.assertEqual(response.data["email"], payload["email"])
        self.assertNotIn("password", response.data)

        created_user = User.objects.get(username=payload["username"])
        self.assertTrue(created_user.check_password(payload["password"]))
        self.assertEqual(response.data["first_name"], payload["first_name"])
        self.assertEqual(response.data["last_name"], payload["last_name"])
