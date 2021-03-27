from datetime import timedelta

from odoo import fields
from odoo.tests.common import TransactionCase


class TestPurchaseOrderLineScheduley(TransactionCase):
    def setUp(self):
        super(TestPurchaseOrderLineScheduley, self).setUp()
        self.purchase_order_obj = self.env["purchase.order"]
        self.purchase_order_line_obj = self.env["purchase.order.line"]

        # Products
        self.product1 = self.env.ref("product.product_product_13")
        self.product2 = self.env.ref("product.product_product_25")

        # Shipment dates
        self.date_planned_1 = fields.datetime.now()
        self.date_planned_2 = self.date_planned_1 + timedelta(days=1)
        self.date_planned_3 = self.date_planned_2 + timedelta(days=1)

        # Purchase Orders
        self.po1 = self.purchase_order_obj.create(
            {"partner_id": self.ref("base.res_partner_3")}
        )
        self.po1_line1 = self.purchase_order_line_obj.create(
            {
                "order_id": self.po1.id,
                "product_id": self.product1.id,
                "product_uom": self.product1.uom_id.id,
                "name": self.product1.name,
                "price_unit": self.product1.standard_price,
                "date_planned": self.date_planned_1,
                "product_qty": 42.0,
            }
        )
        self.po1_line2 = self.purchase_order_line_obj.create(
            {
                "order_id": self.po1.id,
                "product_id": self.product2.id,
                "product_uom": self.product2.uom_id.id,
                "name": self.product2.name,
                "price_unit": self.product2.standard_price,
                "date_planned": self.date_planned_1,
                "product_qty": 12.0,
            }
        )

        self.po2 = self.purchase_order_obj.create(
            {"partner_id": self.ref("base.res_partner_3")}
        )
        self.po2_line1 = self.purchase_order_line_obj.create(
            {
                "order_id": self.po2.id,
                "product_id": self.product1.id,
                "product_uom": self.product1.uom_id.id,
                "name": self.product1.name,
                "price_unit": self.product1.standard_price,
                "date_planned": self.date_planned_1,
                "product_qty": 10.0,
            }
        )
        self.po2_line2 = self.purchase_order_line_obj.create(
            {
                "order_id": self.po2.id,
                "product_id": self.product2.id,
                "product_uom": self.product2.uom_id.id,
                "name": self.product2.name,
                "price_unit": self.product2.standard_price,
                "date_planned": self.date_planned_1,
                "product_qty": 22.0,
            }
        )

    def test_01_purchase_order_schedule(self):
        """
            Create a schedule for a PO line
        """
        # confirm RFQ
        # Check that we have a schedule line by default
        po1_l1_sls = self.po1_line1.schedule_line_ids
        self.assertEquals(len(po1_l1_sls), 1)
        self.assertEquals(po1_l1_sls.date_planned, self.po1_line1.date_planned)
        # Now we create a new schedule line
        ctx = {
            "active_model": "purchase.order.line",
            "active_id": self.po1_line1.id,
            "active_ids": self.po1_line1.ids,
            "default_order_line_id": self.po1_line1.id,
        }
        # When we open the delivery schedule for the PO line we can see
        # That by default there's just one schedule line with the same
        # as the one indicated in the po line.
        wiz = self.env["schedule.order.line"].with_context(ctx).create({})
        self.assertEquals(wiz.order_line_id, self.po1_line1)
        self.assertEquals(len(wiz.item_ids), 1)
        self.assertEquals(wiz.item_ids.date_planned, self.po1_line1.date_planned)
        # We now reduce the quantity on the existing schedule line and
        # create a second schedule line.
        wiz.item_ids.product_qty = 20
        wiz.item_ids = [
            (0, 0, {"date_planned": self.date_planned_2, "product_qty": 22})
        ]
        wiz.update_schedule_lines()
        # Check that we have the correct schedule lines now.
        po1_l1_sls = self.po1_line1.schedule_line_ids
        self.assertEquals(len(po1_l1_sls), 2)
        po1_l1_sl_d1 = po1_l1_sls.filtered(
            lambda l: l.date_planned == self.date_planned_1
        )
        self.assertEquals(po1_l1_sl_d1.product_qty, 20)
        po1_l1_sl_d2 = po1_l1_sls.filtered(
            lambda l: l.date_planned == self.date_planned_2
        )
        self.assertEquals(po1_l1_sl_d2.product_qty, 22)
