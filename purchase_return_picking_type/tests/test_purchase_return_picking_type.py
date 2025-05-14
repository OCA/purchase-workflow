# Copyright 2025 ForgeFlow, S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo.tests.common import Form, TransactionCase


class TestPurchaseReturnCompany(TransactionCase):
    def setUp(self):
        super().setUp()
        self.company = self.env["res.company"].create({"name": "Test Company"})
        self.supplier = self.env["res.partner"].create({"name": "Supplier"})

        # When creating WH, odoo will create default
        # picking types for Receipts/Delivery Orders...
        self.warehouse = self.env["stock.warehouse"].create(
            {
                "name": "Test Warehouse",
                "code": "TWH",
                "company_id": self.company.id,
            }
        )

    def test_purchase_return_picking_type_from(self):
        with Form(
            self.env["purchase.return.order"].with_context(company_id=self.company.id)
        ) as form:
            form.partner_id = self.supplier

        purchase_return_order = form.save()

        self.assertEqual(
            purchase_return_order.picking_type_id.code,
            "incoming",
            "Wrong value in picking type code",
        )
        self.assertEqual(
            purchase_return_order.picking_type_id.name,
            "Receipts",
            "Wrong picking_type_id",
        )
