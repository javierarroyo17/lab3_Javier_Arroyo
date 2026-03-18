from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from billing.models import Barrel, Invoice, InvoiceLine, Provider


User = get_user_model()


class DeleteConstraintsTests(APITestCase):
    def create_provider(self, suffix):
        return Provider.objects.create(
            name=f"Provider {suffix}",
            address=f"Street {suffix}",
            tax_id=f"TAX-{suffix}",
        )

    def test_delete_barrel_returns_400_when_barrel_has_invoice_lines(self):
        provider = self.create_provider("A")
        user = User.objects.create_user(
            username="user_a",
            password="strongpass123",
            provider=provider,
        )
        barrel = Barrel.objects.create(
            provider=provider,
            number="BAR-001",
            oil_type="olive",
            liters=100,
        )
        invoice = Invoice.objects.create(
            provider=provider,
            invoice_no="INV-A-001",
            issued_on=date(2026, 3, 17),
        )
        invoice.add_line_for_barrel(
            barrel=barrel,
            liters=100,
            unit_price_per_liter=Decimal("1.50"),
            description="Initial line",
        )
        self.client.force_authenticate(user=user)

        response = self.client.delete(reverse("barrel-detail", kwargs={"pk": barrel.id}))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)
        self.assertTrue(Barrel.objects.filter(id=barrel.id).exists())
        self.assertEqual(InvoiceLine.objects.count(), 1)
