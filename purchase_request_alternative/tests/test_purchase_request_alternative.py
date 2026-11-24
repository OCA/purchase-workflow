# Copyright 2026 Jarsa
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo import SUPERUSER_ID
from odoo.tests import Form, TransactionCase


class TestPurchaseRequestAlternative(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.vendor_a = cls.env["res.partner"].create(
            {"name": "Vendor A", "is_company": True, "supplier_rank": 1}
        )
        cls.vendor_b = cls.env["res.partner"].create(
            {"name": "Vendor B", "is_company": True, "supplier_rank": 1}
        )
        cls.product = cls.env["product.product"].create(
            {"name": "Test Product", "type": "consu"}
        )
        cls.request = cls.env["purchase.request"].create(
            {
                "picking_type_id": cls.env.ref("stock.picking_type_in").id,
                "requested_by": SUPERUSER_ID,
            }
        )
        cls.request_line = cls.env["purchase.request.line"].create(
            {
                "request_id": cls.request.id,
                "product_id": cls.product.id,
                "product_uom_id": cls.env.ref("uom.product_uom_unit").id,
                "product_qty": 5.0,
            }
        )
        cls.request.button_to_approve()
        cls.request.button_approved()
        wizard = (
            cls.env["purchase.request.line.make.purchase.order"]
            .with_context(
                active_model="purchase.request.line",
                active_ids=cls.request_line.ids,
                active_id=cls.request_line.id,
            )
            .create({"supplier_id": cls.vendor_a.id})
        )
        wizard.make_purchase_order()
        cls.origin_po = cls.request_line.purchase_lines.order_id

    def _create_alternative(self, origin_po, partner, copy_products=True):
        action = origin_po.action_create_alternative()
        wizard = Form(
            self.env["purchase.requisition.create.alternative"].with_context(
                **action["context"]
            )
        )
        wizard.partner_ids.add(partner)
        wizard.copy_products = copy_products
        wizard = wizard.save()
        wizard.action_create_alternative()
        return origin_po.alternative_po_ids.filtered(lambda po: po != origin_po)

    def test_alternative_keeps_request_link(self):
        self.assertEqual(len(self.request_line.purchase_lines), 1)
        alt_po = self._create_alternative(self.origin_po, self.vendor_b)
        self.assertEqual(len(alt_po), 1)
        self.assertEqual(alt_po.partner_id, self.vendor_b)
        alt_line = alt_po.order_line
        self.assertEqual(len(alt_line), 1)
        self.assertEqual(alt_line.purchase_request_lines, self.request_line)
        self.assertEqual(
            self.request_line.purchase_lines, self.origin_po.order_line | alt_line
        )
        allocation = alt_line.purchase_request_allocation_ids
        self.assertEqual(len(allocation), 1)
        self.assertEqual(allocation.purchase_request_line_id, self.request_line)
        self.assertEqual(allocation.requested_product_uom_qty, 5.0)
        self.assertEqual(allocation.product_uom_id, self.request_line.product_uom_id)
        self.assertEqual(len(self.request_line.purchase_request_allocation_ids), 2)
        self.assertEqual(self.request.purchase_count, 2)

    def test_alternative_wins(self):
        alt_po = self._create_alternative(self.origin_po, self.vendor_b)
        alt_po.with_context(skip_alternative_check=True).button_confirm()
        self.origin_po.button_cancel()
        self.assertEqual(alt_po.state, "purchase")
        self.assertEqual(self.request_line.purchase_state, "purchase")
        self.assertEqual(self.request_line.qty_in_progress, 5.0)
        self.assertEqual(self.request_line.qty_cancelled, 0.0)
        subtype = self.env.ref("purchase_request.mt_request_po_confirmed")
        messages = self.request.message_ids.filtered(
            lambda message: message.subtype_id == subtype
        )
        self.assertEqual(len(messages), 1)
        self.assertIn(alt_po.name, messages.body)

    def test_alternative_without_products(self):
        alt_po = self._create_alternative(
            self.origin_po, self.vendor_b, copy_products=False
        )
        self.assertFalse(alt_po.order_line)
        self.assertEqual(len(self.request_line.purchase_lines), 1)

    def test_alternative_without_request(self):
        origin_po = self.env["purchase.order"].create(
            {
                "partner_id": self.vendor_a.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_qty": 3.0,
                            "price_unit": 10.0,
                        },
                    )
                ],
            }
        )
        alt_po = self._create_alternative(origin_po, self.vendor_b)
        self.assertEqual(len(alt_po.order_line), 1)
        self.assertFalse(alt_po.order_line.purchase_request_lines)
        self.assertFalse(alt_po.order_line.purchase_request_allocation_ids)
