# © 2017 Akretion (http://www.akretion.com)
#   @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestPurchaseOrder(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestPurchaseOrder, cls).setUpClass()
        cls.Product = cls.env["product.product"]
        cls.Purchase = cls.env["purchase.order"]
        cls.PurchaseLine = cls.env["purchase.order.line"]

        cls.product_1 = cls.Product.create({"name": "Product", "type": "consu"})

        cls.partner_3 = cls.env.ref("base.res_partner_3")
        cls.partner_3.fop_shipping = 250

    def test_fop_shipping_reached1(self):
        po = self.Purchase.create({"partner_id": self.partner_3.id})
        self.PurchaseLine.create(
            {
                "order_id": po.id,
                "product_id": self.product_1.id,
                "date_planned": fields.Datetime.now(),
                "name": "Test",
                "product_qty": 1.0,
                "product_uom": self.product_1.uom_id.id,
                "price_unit": 100.0,
            }
        )

        self.assertFalse(po.fop_reached)

        with self.assertRaises(UserError) as e, self.env.cr.savepoint():
            po.button_approve()
        self.assertTrue(
            "You cannot confirm a purchase order with amount under "
            "FOP shipping" in e.exception.args[0]
        )

        po.force_order_under_fop = True
        po.button_approve()
        self.assertEqual(po.state, "purchase")

    def test_fop_shipping_reached2(self):
        po = self.Purchase.create({"partner_id": self.partner_3.id})
        self.PurchaseLine.create(
            {
                "order_id": po.id,
                "product_id": self.product_1.id,
                "date_planned": fields.Datetime.now(),
                "name": "Test",
                "product_qty": 10,
                "product_uom": self.product_1.uom_id.id,
                "price_unit": 45,
            }
        )

        self.assertTrue(po.fop_reached)
        po.button_approve()
        self.assertEqual(po.state, "purchase")
