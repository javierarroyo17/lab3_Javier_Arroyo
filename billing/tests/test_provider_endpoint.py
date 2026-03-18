from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from billing.models import Barrel, Provider


User = get_user_model()


class ProviderEndpointTests(APITestCase):
    def create_provider(self, suffix):
        return Provider.objects.create(
            name=f"Provider {suffix}",
            address=f"Street {suffix}",
            tax_id=f"TAX-{suffix}",
        )

    def test_provider_list_returns_all_providers_for_superuser_and_liters_fields(self):
        provider_a = self.create_provider("A")
        provider_b = self.create_provider("B")
        Barrel.objects.create(
            provider=provider_a,
            number="A-001",
            oil_type="olive",
            liters=120,
            billed=True,
        )
        Barrel.objects.create(
            provider=provider_a,
            number="A-002",
            oil_type="sunflower",
            liters=45,
            billed=False,
        )
        admin_user = User.objects.create_superuser(
            username="admin",
            password="strongpass123",
            email="admin@example.com",
        )
        self.client.force_authenticate(user=admin_user)

        response = self.client.get(reverse("provider-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        provider_payload = next(item for item in response.data if item["id"] == provider_a.id)
        self.assertEqual(provider_payload["name"], provider_a.name)
        self.assertEqual(provider_payload["tax_id"], provider_a.tax_id)
        self.assertEqual(provider_payload["billed_liters"], 120)
        self.assertEqual(provider_payload["liters_to_bill"], 45)
        other_payload = next(item for item in response.data if item["id"] == provider_b.id)
        self.assertEqual(other_payload["billed_liters"], 0)
        self.assertEqual(other_payload["liters_to_bill"], 0)

    def test_provider_list_returns_only_user_provider_for_non_superuser(self):
        provider_a = self.create_provider("A")
        self.create_provider("B")
        user = User.objects.create_user(
            username="provider_user",
            password="strongpass123",
            provider=provider_a,
        )
        self.client.force_authenticate(user=user)

        response = self.client.get(reverse("provider-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], provider_a.id)

    def test_provider_detail_returns_data_for_superuser(self):
        provider = self.create_provider("A")
        admin_user = User.objects.create_superuser(
            username="admin",
            password="strongpass123",
            email="admin@example.com",
        )
        self.client.force_authenticate(user=admin_user)

        response = self.client.get(reverse("provider-detail", kwargs={"pk": provider.id}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], provider.id)
        self.assertEqual(response.data["name"], provider.name)
        self.assertEqual(response.data["tax_id"], provider.tax_id)

    def test_provider_detail_returns_403_for_non_superuser(self):
        provider_a = self.create_provider("A")
        user = User.objects.create_user(
            username="provider_user",
            password="strongpass123",
            provider=provider_a,
        )
        self.client.force_authenticate(user=user)

        response = self.client.get(reverse("provider-detail", kwargs={"pk": provider_a.id}))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
