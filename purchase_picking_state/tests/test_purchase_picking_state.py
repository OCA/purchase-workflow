# Copyright 2016 Chafique DELLI @ Akretion
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from odoo.addons.account.tests.account_test_classes import AccountingTestCase


class TestPurchasePickingState(AccountingTestCase):
    def setUp(self):
        super(TestPurchasePickingState, self).setUp()
        # Useful models
        self.PurchaseOrder = self.env["purchase.order"]
        self.StockPicking = self.env["stock.picking"]
        self.partner_id = self.env.ref("base.res_partner_1")
        self.product_id_1 = self.env.ref("product.product_product_8")
        self.product_id_2 = self.env.ref("product.product_product_11")

        (self.product_id_1 | self.product_id_2).write(
            {"purchase_method": "purchase"}
        )
        self.po_vals = {
            "partner_id": self.partner_id.id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "name": self.product_id_1.name,
                        "product_id": self.product_id_1.id,
                        "product_qty": 5.0,
                        "product_uom": self.product_id_1.uom_po_id.id,
                        "price_unit": 500.0,
                        "date_planned": datetime.today().strftime(DTF),
                    },
                ),
                (
                    0,
                    0,
                    {
                        "name": self.product_id_2.name,
                        "product_id": self.product_id_2.id,
                        "product_qty": 5.0,
                        "product_uom": self.product_id_2.uom_po_id.id,
                        "price_unit": 250.0,
                        "date_planned": datetime.today().strftime(DTF),
                    },
                ),
            ],
        }

    def test_picking_state_in_purchase_order(self):
        self.po = self.PurchaseOrder.create(self.po_vals)
        # picking_state equals to draft
        self.assertEqual(self.po.picking_state, "draft")
        # confirm po and picking_state equals to not_received
        self.po.button_confirm()
        self.assertEqual(self.po.picking_state, "not_received")
        # cancel picking and picking_state equals to cancel
        self.po.picking_ids.action_cancel()
        self.assertEqual(self.po.picking_state, "cancel")
        self.po.button_cancel()
        self.po.button_draft()
        self.po.button_confirm()
        pick = self.po.picking_ids.filtered(
            lambda x: x.state not in ("done", "cancel")
        )
        pick.move_line_ids.write({"qty_done": 2})
        pick.action_done()
        self.assertEqual(self.po.picking_state, "partially_received")
        backorders = self.StockPicking.search([("backorder_id", "=", pick.id)])
        backorders.move_line_ids.write({"qty_done": 3})
        backorders.action_done()
        self.assertEqual(self.po.picking_state, "done")
