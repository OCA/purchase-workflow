# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo.tests import Form, TransactionCase


class TestPurchaseReceiptProgress(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.po_partner = cls.env["res.partner"].create({"name": "Partner 1"})
        cls.po_product = cls.env["product.product"].create(
            {"name": "Product", "type": "product"}
        )
        cls.order_vals = {
            "partner_id": cls.po_partner.id,
            "company_id": cls.env.user.company_id.id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "name": cls.po_product.name,
                        "product_id": cls.po_product.id,
                        "product_qty": 10.0,
                        "product_uom": cls.po_product.uom_po_id.id,
                        "price_unit": 10.0,
                        "date_planned": datetime.today(),
                    },
                )
            ],
        }

    def test_00_half_receipt(self):
        """Testing a receipt expectation of "half" on a purchase order`

        Steps:
            - Create a standard purchase order
            - Confirm it
            - Create a receipt for the order with 5 units, then test

        Expect:
            - The order should show a receipt expectation of 50% on delivery_status field
        """
        order = self.env["purchase.order"].create(self.order_vals)
        order.button_confirm()
        self.assertTrue(order.picking_ids)
        picking = order.picking_ids
        picking.action_assign()
        picking.move_line_ids.write({"qty_done": 5})
        picking.button_validate()
        backorder_wizard_dict = picking.button_validate()
        backorder_wizard = Form(
            self.env[backorder_wizard_dict["res_model"]].with_context(
                **backorder_wizard_dict["context"]
            )
        ).save()
        backorder_wizard.process()
        self.assertEqual(order.delivery_status, 0.5)

    def test_00_full_receipt(self):
        """Testing a receipt full on a purchase order`

        Steps:
            - Create a standard purchase order
            - Confirm it
            - Create a receipt for the order with 10 units, then test

        Expect:
            - The order should show a receipt expectation of 100% on delivery_status field
        """
        order = self.env["purchase.order"].create(self.order_vals)
        order.button_confirm()
        self.assertTrue(order.picking_ids)
        picking = order.picking_ids
        picking.action_assign()
        picking.move_line_ids.write({"qty_done": 10})
        picking.button_validate()
        self.assertEqual(order.delivery_status, 1)
