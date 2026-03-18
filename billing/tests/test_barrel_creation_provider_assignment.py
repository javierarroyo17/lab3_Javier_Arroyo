from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from billing.models import Barrel, Provider


User = get_user_model()


class BarrelCreationProviderAssignmentTests(APITestCase):
    def create_provider(self, suffix):
        return Provider.objects.create(
            name=f"Provider {suffix}",
            address=f"Street {suffix}",
            tax_id=f"TAX-{suffix}",
        )

    def test_barrel_creation_forces_provider_from_logged_in_user(self):
        provider_a = self.create_provider("A")
        provider_b = self.create_provider("B")
        user_a = User.objects.create_user(
            username="user_a",
            password="strongpass123",
            provider=provider_a,
        )
        self.client.force_authenticate(user=user_a)

        response = self.client.post(
            reverse("barrel-list"),
            {
                "provider": provider_b.id,
                "number": "BAR-001",
                "oil_type": "olive",
                "liters": 200,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["provider"], provider_a.id)
        barrel = Barrel.objects.get(id=response.data["id"])
        self.assertEqual(barrel.provider_id, provider_a.id)
