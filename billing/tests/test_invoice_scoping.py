from datetime import date

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from billing.models import Invoice, Provider


User = get_user_model()


class InvoiceScopingTests(APITestCase):
    def create_provider(self, suffix):
        return Provider.objects.create(
            name=f"Provider {suffix}",
            address=f"Street {suffix}",
            tax_id=f"TAX-{suffix}",
        )

    def create_invoice(self, provider, suffix):
        return Invoice.objects.create(
            provider=provider,
            invoice_no=f"INV-{suffix}",
            issued_on=date(2026, 3, 17),
        )

    def test_invoice_list_returns_only_invoices_of_logged_in_user_provider(self):
        provider_a = self.create_provider("A")
        provider_b = self.create_provider("B")
        invoice_a = self.create_invoice(provider_a, "A-001")
        self.create_invoice(provider_b, "B-001")
        user_a = User.objects.create_user(
            username="user_a",
            password="strongpass123",
            provider=provider_a,
        )
        self.client.force_authenticate(user=user_a)

        response = self.client.get(reverse("invoice-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], invoice_a.id)
        self.assertEqual(response.data[0]["provider"], provider_a.id)

    def test_invoice_detail_returns_404_for_invoice_of_other_provider(self):
        provider_a = self.create_provider("A")
        provider_b = self.create_provider("B")
        invoice_b = self.create_invoice(provider_b, "B-001")
        user_a = User.objects.create_user(
            username="user_a",
            password="strongpass123",
            provider=provider_a,
        )
        self.client.force_authenticate(user=user_a)

        response = self.client.get(reverse("invoice-detail", kwargs={"pk": invoice_b.id}))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
