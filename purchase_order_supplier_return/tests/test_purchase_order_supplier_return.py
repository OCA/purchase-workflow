# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.tests.common import TransactionCase

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


class TestPurchaseOrderSupplierReturn(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env["base"].with_context(**DISABLED_MAIL_CONTEXT).env
        cls.product = cls.env["product.product"].create(
            {"name": "Product Test", "list_price": 5.0}
        )
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Partner",
            }
        )
        cls.purchase_order = cls.env["purchase.order"].create(
            {
                "partner_id": cls.partner.id,
            }
        )
        cls.purchase_order_line_1 = cls.env["purchase.order.line"].create(
            {
                "order_id": cls.purchase_order.id,
                "product_id": cls.product.id,
                "product_qty": -1,
            }
        )
        cls.purchase_order_line_2 = cls.env["purchase.order.line"].create(
            {
                "order_id": cls.purchase_order.id,
                "product_id": cls.product.id,
                "product_qty": 1,
            }
        )

    def test_negative_purchase_order_line(self):
        """Test that the negative purchase_order_line is correctly received
        with the negative quantity when the related picking is validated."""
        self.purchase_order.button_confirm()
        self.assertEqual(self.purchase_order.order_line[0].qty_received, 0)

        # Validate the pickings related to the purchase order
        for picking in self.purchase_order.picking_ids:
            picking.action_set_quantities_to_reservation()
            picking.button_validate()
        self.assertTrue(
            self.purchase_order.order_line[0].move_ids._is_purchase_return()
        )
        self.assertTrue(self.purchase_order.order_line[0].move_ids.to_refund)
        self.assertEqual(self.purchase_order.order_line[0].qty_received, -1)

        self.assertFalse(
            self.purchase_order.order_line[1].move_ids._is_purchase_return()
        )
        self.assertFalse(self.purchase_order.order_line[1].move_ids.to_refund)
        self.assertEqual(self.purchase_order.order_line[1].qty_received, 1)
