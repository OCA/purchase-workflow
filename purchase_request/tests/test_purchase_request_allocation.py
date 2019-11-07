# Copyright 2018-2019 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo.tests import common
from odoo.tools import SUPERUSER_ID


class TestPurchaseRequestToRfq(common.TransactionCase):
    def setUp(self):
        super(TestPurchaseRequestToRfq, self).setUp()
        self.purchase_request = self.env["purchase.request"]
        self.purchase_request_line = self.env["purchase.request.line"]
        self.wiz = self.env["purchase.request.line.make.purchase.order"]
        self.purchase_order = self.env["purchase.order"]
        vendor = self.env["res.partner"].create({"name": "Partner #2"})
        self.service_product = self.env["product.product"].create(
            {"name": "Product Service Test", "type": "service"}
        )
        self.product_product = self.env["product.product"].create(
            {"name": "Product Product Test", "type": "product"}
        )
        self.env["product.supplierinfo"].create(
            {
                "name": vendor.id,
                "product_tmpl_id": self.service_product.product_tmpl_id.id,
            }
        )
        self.env["product.supplierinfo"].create(
            {
                "name": vendor.id,
                "product_tmpl_id": self.product_product.product_tmpl_id.id,
            }
        )

    def create_purchase_request(self, product=None):
        """ Returns an post invoice """
        purchase = self.purchase_request.create(
            {
                "picking_type_id": self.env.ref("stock.picking_type_in").id,
                "requested_by": SUPERUSER_ID,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "product_uom_id": self.env.ref("uom.product_uom_unit").id,
                            "product_qty": 2.0,
                        },
                    )
                ],
            }
        )
        purchase.button_to_approve()
        purchase.button_approved()
        return purchase

    def test_purchase_request_allocation(self):
        purchase_request1 = self.create_purchase_request(product=self.product_product)
        self.assertEqual(purchase_request1.state, "approved")
        purchase_request2 = self.create_purchase_request(product=self.product_product)
        self.assertEqual(purchase_request2.state, "approved")
        vals = {"supplier_id": self.env.ref("base.res_partner_1").id}
        purchase_request_line1 = self.purchase_request_line.search(
            [("request_id", "=", purchase_request1.id)]
        )
        purchase_request_line2 = self.purchase_request_line.search(
            [("request_id", "=", purchase_request2.id)]
        )
        wiz_id = self.wiz.with_context(
            active_model="purchase.request.line",
            active_ids=[purchase_request_line1.id, purchase_request_line2.id],
        ).create(vals)
        wiz_id.make_purchase_order()
        purchase = purchase_request_line1.purchase_lines[0].order_id
        purchase.button_confirm()
        self.assertEqual(purchase_request_line1.qty_in_progress, 2.0)
        self.assertEqual(purchase_request_line2.qty_in_progress, 2.0)
        picking = purchase.picking_ids[0]
        picking.move_line_ids[0].write({"qty_done": 2.0})
        backorder_wiz_id = picking.button_validate()["res_id"]
        backorder_wiz = self.env["stock.backorder.confirmation"].browse(
            [backorder_wiz_id]
        )
        backorder_wiz.process()
        self.assertEqual(purchase_request_line1.qty_done, 2.0)
        self.assertEqual(purchase_request_line2.qty_done, 0.0)

        backorder_picking = purchase.picking_ids.filtered(lambda p: p.id != picking.id)
        backorder_picking.move_line_ids[0].write({"qty_done": 1.0})
        backorder_wiz_id2 = backorder_picking.button_validate()["res_id"]
        backorder_wiz2 = self.env["stock.backorder.confirmation"].browse(
            [backorder_wiz_id2]
        )
        backorder_wiz2.process()

        self.assertEqual(purchase_request_line1.qty_done, 2.0)
        self.assertEqual(purchase_request_line2.qty_done, 1.0)
        for pick in purchase.picking_ids:
            if pick.state == "assigned":
                pick.action_cancel()
        self.assertEqual(purchase_request_line1.qty_cancelled, 0.0)
        self.assertEqual(purchase_request_line2.qty_cancelled, 1.0)
        self.assertEqual(purchase_request_line1.pending_qty_to_receive, 0.0)
        self.assertEqual(purchase_request_line2.pending_qty_to_receive, 1.0)

    def test_purchase_request_allocation_services(self):
        purchase_request1 = self.create_purchase_request(product=self.service_product)
        self.assertEqual(purchase_request1.state, "approved")
        purchase_request_line1 = self.purchase_request_line.search(
            [("request_id", "=", purchase_request1.id)]
        )
        vals = {"supplier_id": self.env.ref("base.res_partner_1").id}
        purchase_request1.button_approved()
        wiz_id = self.wiz.with_context(
            active_model="purchase.request.line", active_ids=[purchase_request_line1.id]
        ).create(vals)
        wiz_id.make_purchase_order()
        purchase = purchase_request_line1.purchase_lines[0].order_id
        purchase.button_confirm()
        self.assertEqual(purchase_request_line1.qty_in_progress, 2.0)
        # manually set in the PO line
        purchase_request_line1.purchase_lines[0].write({"qty_received": 0.5})
        self.assertEqual(purchase_request_line1.qty_done, 0.5)
        purchase.button_cancel()
        self.assertEqual(purchase_request_line1.qty_cancelled, 1.5)
        self.assertEqual(purchase_request_line1.pending_qty_to_receive, 1.5)

    def test_purchase_request_allocation_min_qty(self):
        purchase_request1 = self.create_purchase_request(product=self.product_product)
        self.assertEqual(purchase_request1.state, "approved")
        purchase_request_line1 = self.purchase_request_line.search(
            [("request_id", "=", purchase_request1.id)]
        )
        # add a vendor
        vendor1 = self.env.ref("base.res_partner_1")
        self.env["product.supplierinfo"].create(
            {
                "name": vendor1.id,
                "product_tmpl_id": self.product_product.product_tmpl_id.id,
                "min_qty": 8,
            }
        )
        vals = {"supplier_id": self.env.ref("base.res_partner_1").id}
        purchase_request1.button_approved()
        wiz_id = self.wiz.with_context(
            active_model="purchase.request.line", active_ids=[purchase_request_line1.id]
        ).create(vals)
        wiz_id.make_purchase_order()
        self.assertEqual(
            purchase_request_line1.purchase_request_allocation_ids[0].open_product_qty,
            2.0,
        )
        self.assertEqual(purchase_request_line1.purchased_qty, 8)
