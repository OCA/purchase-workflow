# Copyright 2019 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.fields import Datetime
from odoo.tests.common import TransactionCase


class TestPurchaseReceptionNotify(TransactionCase):
    def setUp(self):
        super(TestPurchaseReceptionNotify, self).setUp()
        self.purchase_order_model = self.env["purchase.order"]
        purchase_order_line_model = self.env["purchase.order.line"]
        partner_model = self.env["res.partner"]
        prod_model = self.env["product.product"]
        self.product_uom_model = self.env["uom.uom"]

        # partners
        pa_dict = {"name": "Partner 1"}
        self.partner = partner_model.sudo().create(pa_dict)

        # Purchase Order Num 1
        po_dict = {"partner_id": self.partner.id}
        self.purchase_order = self.purchase_order_model.create(po_dict)
        uom_id = self.env.ref("uom.product_uom_unit").id
        pr_dict = {
            "name": "Product Test",
            "uom_id": uom_id,
            "purchase_method": "purchase",
        }
        self.product = prod_model.sudo().create(pr_dict)
        pl_dict1 = {
            "date_planned": Datetime.now(),
            "name": "PO01",
            "order_id": self.purchase_order.id,
            "product_id": self.product.id,
            "product_uom": uom_id,
            "price_unit": 1.0,
            "product_qty": 5.0,
        }
        self.purchase_order_line = purchase_order_line_model.sudo().create(pl_dict1)
        self.purchase_order.button_confirm()

    def test_reception_notification(self):
        # Now we receive the products
        for picking in self.purchase_order.picking_ids:
            picking.move_lines.write({"quantity_done": 5.0})
            picking.button_validate()
            self.assertTrue(
                "Receipt confirmation %s" % picking.name
                in self.purchase_order_line.order_id.message_ids[0].body,
                "PO user not notified",
            )
