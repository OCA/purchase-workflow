# Copyright 2020 Camptocamp SA
# Copyright 2020 ForgeFlow, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import TransactionCase


class TestPurchaseOrderLinePackagingQty(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner = cls.env.ref("base.res_partner_12")
        cls.product = cls.env.ref("product.product_product_9")
        cls.packaging = cls.env["product.packaging"].create(
            {"name": "Test packaging", "product_id": cls.product.id, "qty": 5.0}
        )
        cls.packaging_12 = cls.env["product.packaging"].create(
            {"name": "Test packaging 12", "product_id": cls.product.id, "qty": 12.0}
        )

    def test_product_packaging_qty(self):
        order = self.env["purchase.order"].create({"partner_id": self.partner.id})
        order_line = self.env["purchase.order.line"].create(
            {
                "name": self.product.display_name,
                "order_id": order.id,
                "product_id": self.product.id,
                "product_uom": self.product.uom_id.id,
                "product_qty": 3.0,
                "price_unit": 0.0,
                "date_planned": fields.Datetime.today(),
            }
        )
        order_line.write({"product_packaging": self.packaging})
        order_line._onchange_product_packaging()
        self.assertEqual(order_line.product_uom_qty, 5.0)
        self.assertEqual(order_line.product_packaging_qty, 1.0)
        order_line.write({"product_packaging_qty": 3.0})
        self.assertEqual(order_line.product_uom_qty, 15.0)

        # Remove product packaging
        order_line.update({"product_packaging": False})
        order_line._onchange_product_packaging()
        self.assertEqual(0.0, order_line.product_packaging_qty)

    def test_product_packaging_qty_0(self):
        # Don't mention packaging
        # Check if packaging quantity == 0
        order = self.env["purchase.order"].create({"partner_id": self.partner.id})
        order_line = self.env["purchase.order.line"].create(
            {
                "name": self.product.display_name,
                "order_id": order.id,
                "product_id": self.product.id,
                "product_uom": self.product.uom_id.id,
                "product_qty": 3.0,
                "price_unit": 0.0,
                "date_planned": fields.Datetime.today(),
            }
        )
        order_line._onchange_product_packaging()
        self.assertEqual(0.0, order_line.product_packaging_qty)

    def test_product_packaging_qty_with_unit(self):
        # Check packaging quantity with a different unit of measure
        # on purchase order line than product
        dozen = self.env.ref("uom.product_uom_dozen")
        order = self.env["purchase.order"].create({"partner_id": self.partner.id})
        order_line = self.env["purchase.order.line"].create(
            {
                "name": self.product.display_name,
                "order_id": order.id,
                "product_id": self.product.id,
                "product_uom": dozen.id,
                "product_qty": 1.0,
                "price_unit": 0.0,
                "date_planned": fields.Datetime.today(),
            }
        )
        order_line.write({"product_packaging": self.packaging_12.id})
        order_line._onchange_product_packaging()
        self.assertEqual(12.0, order_line.product_uom_qty)
        self.assertEqual(1.0, order_line.product_packaging_qty)

    def test_product_packaging_qty_inverse(self):
        # Try to change product packaging quantity without having chosen packaging
        order = self.env["purchase.order"].create({"partner_id": self.partner.id})
        order_line = self.env["purchase.order.line"].create(
            {
                "name": self.product.display_name,
                "order_id": order.id,
                "product_id": self.product.id,
                "product_uom": self.product.uom_id.id,
                "product_qty": 3.0,
                "price_unit": 0.0,
                "date_planned": fields.Datetime.today(),
            }
        )
        msg = "You must define a package before setting a quantity"
        with self.assertRaises(UserError, msg=msg):
            order_line.write({"product_packaging_qty": 1.0})

    def test_product_packaging_qty_onchange(self):
        # Try to change product packaging quantity and check values
        order = self.env["purchase.order"].create({"partner_id": self.partner.id})
        order_line = self.env["purchase.order.line"].create(
            {
                "name": self.product.display_name,
                "order_id": order.id,
                "product_id": self.product.id,
                "product_uom": self.product.uom_id.id,
                "product_qty": 3.0,
                "price_unit": 0.0,
                "date_planned": fields.Datetime.today(),
            }
        )
        order_line.write({"product_packaging": self.packaging_12.id})
        order_line._onchange_product_packaging()

        order_line.update({"product_packaging_qty": 2.0})
        self.assertEqual(24.0, order_line.product_uom_qty)

    def test_change_product_quantity(self):
        # Try to change product packaging quantity and check values
        order = self.env["purchase.order"].create({"partner_id": self.partner.id})
        order_line = self.env["purchase.order.line"].create(
            {
                "name": self.product.display_name,
                "order_id": order.id,
                "product_id": self.product.id,
                "product_uom": self.product.uom_id.id,
                "product_qty": 1.0,
                "price_unit": 0.0,
                "date_planned": fields.Datetime.today(),
            }
        )
        order_line.write({"product_packaging": self.packaging_12.id})
        order_line._onchange_product_packaging()

        order_line.update({"product_qty": 5.0})

        res = order_line._onchange_quantity()
        self.assertIn(
            "warning",
            res,
        )
