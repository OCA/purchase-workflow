# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests.common import TransactionCase


class TestPurchaseCompanyInvoiceAddress(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company_partner = cls.env.company.partner_id
        cls.vendor = cls.env["res.partner"].create({"name": "Test Vendor"})
        cls.product = cls.env["product.product"].create(
            {"name": "Test Service", "type": "service"}
        )

    def _create_purchase_order(self):
        return self.env["purchase.order"].create(
            {
                "partner_id": self.vendor.id,
                "order_line": [
                    Command.create({"product_id": self.product.id, "product_qty": 1.0})
                ],
            }
        )

    def _create_invoice_address(self):
        return self.env["res.partner"].create(
            {
                "name": "Branch",
                "parent_id": self.company_partner.id,
                "type": "invoice",
            }
        )

    def test_default_without_invoice_address(self):
        """Without a dedicated address, the company partner itself is proposed."""
        order = self._create_purchase_order()
        self.assertEqual(order.company_invoice_address_id, self.company_partner)

    def test_default_with_invoice_address(self):
        """An invoice address of the company is proposed once one exists."""
        address = self._create_invoice_address()
        order = self._create_purchase_order()
        self.assertEqual(order.company_invoice_address_id, address)
