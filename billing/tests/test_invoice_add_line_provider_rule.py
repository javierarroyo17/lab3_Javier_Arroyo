from datetime import date

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from billing.models import Barrel, Invoice, InvoiceLine, Provider


User = get_user_model()


class InvoiceAddLineProviderRuleTests(APITestCase):
    def create_provider(self, suffix):
        return Provider.objects.create(
            name=f"Provider {suffix}",
            address=f"Street {suffix}",
            tax_id=f"TAX-{suffix}",
        )

    def test_add_line_returns_400_when_barrel_provider_differs_from_invoice_provider(self):
        provider_a = self.create_provider("A")
        provider_b = self.create_provider("B")
        user_a = User.objects.create_user(
            username="user_a",
            password="strongpass123",
            provider=provider_a,
        )
        invoice_a = Invoice.objects.create(
            provider=provider_a,
            invoice_no="INV-A-001",
            issued_on=date(2026, 3, 17),
        )
        barrel_b = Barrel.objects.create(
            provider=provider_b,
            number="B-001",
            oil_type="olive",
            liters=100,
            billed=False,
        )
        self.client.force_authenticate(user=user_a)

        response = self.client.post(
            reverse("invoice-add-line", kwargs={"pk": invoice_a.id}),
            {
                "barrel": barrel_b.id,
                "liters": barrel_b.liters,
                "description": "Line with invalid provider",
                "unit_price": "1.50",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)
        self.assertIn(
            "barrel provider must match invoice provider",
            str(response.data["detail"]),
        )
        self.assertEqual(InvoiceLine.objects.count(), 0)
        barrel_b.refresh_from_db()
        self.assertFalse(barrel_b.billed)
