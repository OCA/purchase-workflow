from datetime import timedelta

from odoo import fields
from odoo.tests.common import TransactionCase


class TestPurchaseOrderLineScheduleManualDelivery(TransactionCase):
    def setUp(self):
        super(TestPurchaseOrderLineScheduleManualDelivery, self).setUp()
        self.purchase_order_obj = self.env["purchase.order"]
        self.purchase_order_line_obj = self.env["purchase.order.line"]
        self.stock_picking_obj = self.env["stock.picking"]

        # Products
        self.product1 = self.env.ref("product.product_product_13")
        self.product2 = self.env.ref("product.product_product_25")

        # Sublocation
        self.shelf2 = self.env.ref("stock.stock_location_14")

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

    def test_01_purchase_order_manual_delivery(self):
        """
            Confirm Purchase Order 1, check no incoming shipments have been
            pre-created, create them manually (create one with one PO line,
            add second PO line to same picking afterwards)
        """
        # confirm RFQ
        self.po1.button_confirm_manual()
        self.assertFalse(
            self.po1.picking_ids,
            "Purchase Manual Delivery: no picking should had been created",
        )
        # Create a delivery schedule
        ctx = {
            "active_model": "purchase.order",
            "active_id": self.po1.id,
            "active_ids": self.po1.ids,
            "default_order_id": self.po1.id,
        }
        schedule_wiz = self.env["schedule.purchase.order"].with_context(ctx).create({})
        # Check that by default the wizard only proposes one scheduled date
        for sd in schedule_wiz.schedule_date_ids:
            self.assertIn(sd.date_planned, [self.date_planned_1])
            # We have 2 order lines with the same scheduled date
            self.assertEquals(sd.count_schedule_lines, 2)
        # Create a new schedule date
        schedule_wiz.schedule_date_ids = [(0, 0, {"date_planned": self.date_planned_2})]
        res = schedule_wiz.create_schedule_grid()
        self.assertIn("res_id", res.keys())
        grid = self.env["schedule.purchase.order.grid"].browse(res["res_id"])
        # We have a matrix of 2 x 2
        self.assertEquals(len(grid.line_ids), 4)
        grid_po1_line_1 = grid.line_ids.filtered(
            lambda l: l.order_line_id == self.po1_line1
        )
        grid_po1_line_1_dt1 = grid_po1_line_1.filtered(
            lambda l: l.date_planned == self.date_planned_1
        )
        self.assertEquals(grid_po1_line_1_dt1.product_qty, self.po1_line1.product_qty)
        grid_po1_line_1_dt2 = grid_po1_line_1.filtered(
            lambda l: l.date_planned == self.date_planned_2
        )
        self.assertEquals(grid_po1_line_1_dt2.product_qty, 0.0)
        # Update the matrix so as to put some quantities in date 2 for po line 1
        grid_po1_line_1_dt1.product_qty = 20
        grid_po1_line_1_dt2.product_qty = 22
        # Close the wizard to update the schedule lines.
        grid.update_schedule_lines()
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
        po1_l2_sls = self.po1_line2.schedule_line_ids
        self.assertEquals(len(po1_l2_sls), 1)
        self.assertEquals(po1_l2_sls.product_qty, 12)
        # Create an incoming shipment for date 1, where we expect
        # to receive 20 units of po 1 line 1 and all units of po 1 line 2
        wizard = (
            self.env["create.stock.picking.wizard"]
            .with_context(
                {
                    "active_model": "purchase.order",
                    "active_id": self.po1.id,
                    "active_ids": self.po1.ids,
                }
            )
            .create({})
        )
        wizard.fill_schedule_lines(self.po1.order_line.mapped("schedule_line_ids"))
        wizard.schedule_line_ids = wizard.schedule_line_ids.filtered(
            lambda l: l.date_planned == self.date_planned_1
        )
        wizard.create_stock_picking()
        # check picking is created
        self.assertTrue(
            self.po1.picking_ids,
            'Purchase Manual Delivery: picking \
            should be created after "manual delivery" wizard call',
        )
        picking = self.po1.picking_ids[0]
        self.assertEquals(picking.scheduled_date, self.date_planned_1)
        # The picking has two stock moves
        self.assertEquals(len(picking.move_lines), 2)
        move_product_1 = picking.move_lines.filtered(
            lambda m: m.product_id == self.product1
        )
        # The quantities in the moves match with the quantities that we
        # indicated to move to an incoming shipment.
        self.assertEquals(move_product_1.product_uom_qty, 20)
        move_product_2 = picking.move_lines.filtered(
            lambda m: m.product_id == self.product2
        )
        self.assertEquals(move_product_2.product_uom_qty, 12)
        # The po 1 line 1 reflects now the correct quantity being received
        self.assertEquals(self.po1_line1.qty_in_receipt, 20)
        self.assertEquals(self.po1_line2.qty_in_receipt, 12)
        # Now we reschedule the pending quantity in po 1 line 1
        # Create a delivery schedule
        ctx = {
            "active_model": "purchase.order",
            "active_id": self.po1.id,
            "active_ids": self.po1.ids,
            "default_order_id": self.po1.id,
        }
        schedule_wiz = self.env["schedule.purchase.order"].with_context(ctx).create({})
        # Check that by default the wizard now proposes two scheduled dates
        for dp in schedule_wiz.schedule_date_ids.mapped("date_planned"):
            self.assertIn(dp, [self.date_planned_1, self.date_planned_2])
        # Create a new schedule date
        schedule_wiz.schedule_date_ids = [(0, 0, {"date_planned": self.date_planned_3})]
        res = schedule_wiz.create_schedule_grid()
        self.assertIn("res_id", res.keys())
        grid = self.env["schedule.purchase.order.grid"].browse(res["res_id"])
        # Considering that we have added a new date,
        # We expect to have a matrix of 2 x 3
        self.assertEquals(len(grid.line_ids), 6)
        grid_po1_line_1 = grid.line_ids.filtered(
            lambda l: l.order_line_id == self.po1_line1
        )
        grid_po1_line_1_dt1 = grid_po1_line_1.filtered(
            lambda l: l.date_planned == self.date_planned_1
        )
        self.assertEquals(grid_po1_line_1_dt1.product_qty, 0.0)
        grid_po1_line_1_dt2 = grid_po1_line_1.filtered(
            lambda l: l.date_planned == self.date_planned_2
        )
        self.assertEquals(grid_po1_line_1_dt2.product_qty, 22.0)
        grid_po1_line_1_dt3 = grid_po1_line_1.filtered(
            lambda l: l.date_planned == self.date_planned_3
        )
        self.assertEquals(grid_po1_line_1_dt3.product_qty, 0.0)
        grid_po1_line_2 = grid.line_ids.filtered(
            lambda l: l.order_line_id == self.po1_line2
        )
        grid_po1_line_2_dt1 = grid_po1_line_2.filtered(
            lambda l: l.date_planned == self.date_planned_1
        )
        self.assertEquals(grid_po1_line_2_dt1.product_qty, 0.0)
        grid_po1_line_2_dt2 = grid_po1_line_2.filtered(
            lambda l: l.date_planned == self.date_planned_2
        )
        self.assertEquals(grid_po1_line_2_dt2.product_qty, 0.0)
        grid_po1_line_2_dt3 = grid_po1_line_2.filtered(
            lambda l: l.date_planned == self.date_planned_3
        )
        self.assertEquals(grid_po1_line_2_dt3.product_qty, 0.0)
        # Update the matrix so as to put some quantities in date 3 for po
        # line 1
        grid_po1_line_1_dt2.product_qty = 10
        grid_po1_line_1_dt3.product_qty = 12
        # Close the wizard to update the schedule lines.
        grid.update_schedule_lines()
        # Check that we have the correct schedule lines now.
        po1_l1_sls = self.po1_line1.schedule_line_ids
        self.assertEquals(len(po1_l1_sls), 3)
        po1_l1_sl_d1 = po1_l1_sls.filtered(
            lambda l: l.date_planned == self.date_planned_1
        )
        self.assertEquals(po1_l1_sl_d1.product_qty, 20.0)
        self.assertEquals(po1_l1_sl_d1.qty_in_receipt, 20.0)
        self.assertEquals(po1_l1_sl_d1.qty_received, 0.0)
        po1_l1_sl_d2 = po1_l1_sls.filtered(
            lambda l: l.date_planned == self.date_planned_2
        )
        self.assertEquals(po1_l1_sl_d2.product_qty, 10.0)
        self.assertEquals(po1_l1_sl_d2.qty_in_receipt, 0.0)
        self.assertEquals(po1_l1_sl_d2.qty_received, 0.0)
        po1_l1_sl_d3 = po1_l1_sls.filtered(
            lambda l: l.date_planned == self.date_planned_3
        )
        self.assertEquals(po1_l1_sl_d3.product_qty, 12.0)
        self.assertEquals(po1_l1_sl_d3.qty_in_receipt, 0.0)
        self.assertEquals(po1_l1_sl_d3.qty_received, 0.0)
        po1_l2_sls = self.po1_line2.schedule_line_ids
        self.assertEquals(len(po1_l2_sls), 1.0)
        self.assertEquals(po1_l2_sls.product_qty, 12.0)
        self.assertEquals(po1_l2_sls.qty_in_receipt, 12.0)
        self.assertEquals(po1_l2_sls.qty_received, 0.0)
        # Create an incoming shipment for date 2, where we expect
        # to receive 10 units of po 1 line 1
        wizard = (
            self.env["create.stock.picking.wizard"]
            .with_context(
                {
                    "active_model": "purchase.order",
                    "active_id": self.po1.id,
                    "active_ids": self.po1.ids,
                }
            )
            .create({})
        )
        wizard.fill_schedule_lines(self.po1.order_line.mapped("schedule_line_ids"))
        wizard.schedule_line_ids = wizard.schedule_line_ids.filtered(
            lambda l: l.date_planned == self.date_planned_2
        )
        wizard.create_stock_picking()
        # check picking is created
        self.assertEquals(len(self.po1.picking_ids), 2)
        picking = self.po1.picking_ids.filtered(
            lambda p: p.scheduled_date == self.date_planned_2
        )
        self.assertEquals(len(picking), 1)
        # Check that we have the correct schedule lines.
        po1_l1_sls = self.po1_line1.schedule_line_ids
        po1_l1_sl_d1 = po1_l1_sls.filtered(
            lambda l: l.date_planned == self.date_planned_1
        )
        self.assertEquals(po1_l1_sl_d1.product_qty, 20.0)
        self.assertEquals(po1_l1_sl_d1.qty_in_receipt, 20.0)
        self.assertEquals(po1_l1_sl_d1.qty_received, 0.0)
        po1_l1_sl_d2 = po1_l1_sls.filtered(
            lambda l: l.date_planned == self.date_planned_2
        )
        self.assertEquals(po1_l1_sl_d2.product_qty, 10.0)
        self.assertEquals(po1_l1_sl_d2.qty_in_receipt, 10.0)
        self.assertEquals(po1_l1_sl_d2.qty_received, 0.0)
        po1_l1_sl_d3 = po1_l1_sls.filtered(
            lambda l: l.date_planned == self.date_planned_3
        )
        self.assertEquals(po1_l1_sl_d3.product_qty, 12.0)
        self.assertEquals(po1_l1_sl_d3.qty_in_receipt, 0.0)
        self.assertEquals(po1_l1_sl_d3.qty_received, 0.0)
        po1_l2_sls = self.po1_line2.schedule_line_ids
        self.assertEquals(len(po1_l2_sls), 1.0)
        self.assertEquals(po1_l2_sls.product_qty, 12.0)
        self.assertEquals(po1_l2_sls.qty_in_receipt, 12.0)
        self.assertEquals(po1_l2_sls.qty_received, 0.0)
        # Complete the first picking
        picking = self.po1.picking_ids.filtered(
            lambda p: p.scheduled_date == self.date_planned_1
        )
        for move in picking.move_lines:
            move.quantity_done = move.product_uom_qty
        picking.action_done()
        # Check that we have the correct schedule lines.
        self.po1_line1.refresh()
        po1_l1_sls = self.po1_line1.schedule_line_ids
        po1_l1_sl_d1 = po1_l1_sls.filtered(
            lambda l: l.date_planned == self.date_planned_1
        )
        self.assertEquals(po1_l1_sl_d1.product_qty, 20.0)
        self.assertEquals(po1_l1_sl_d1.qty_in_receipt, 0.0)
        self.assertEquals(po1_l1_sl_d1.qty_received, 20.0)
        po1_l1_sl_d2 = po1_l1_sls.filtered(
            lambda l: l.date_planned == self.date_planned_2
        )
        self.assertEquals(po1_l1_sl_d2.product_qty, 10.0)
        self.assertEquals(po1_l1_sl_d2.qty_in_receipt, 10.0)
        self.assertEquals(po1_l1_sl_d2.qty_received, 0.0)
        po1_l1_sl_d3 = po1_l1_sls.filtered(
            lambda l: l.date_planned == self.date_planned_3
        )
        self.assertEquals(po1_l1_sl_d3.product_qty, 12.0)
        self.assertEquals(po1_l1_sl_d3.qty_in_receipt, 0.0)
        self.assertEquals(po1_l1_sl_d3.qty_received, 0.0)
        po1_l2_sls = self.po1_line2.schedule_line_ids
        self.assertEquals(len(po1_l2_sls), 1.0)
        self.assertEquals(po1_l2_sls.product_qty, 12.0)
        self.assertEquals(po1_l2_sls.qty_in_receipt, 0.0)
        self.assertEquals(po1_l2_sls.qty_received, 12.0)
