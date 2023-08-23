# Copyright 2019 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestPurchaseManualDelivery(TransactionCase):
    def setUp(self):
        super(TestPurchaseManualDelivery, self).setUp()
        self.purchase_order_obj = self.env["purchase.order"]
        self.purchase_order_line_obj = self.env["purchase.order.line"]
        self.stock_picking_obj = self.env["stock.picking"]
        self.env.company.purchase_manual_delivery = True
        # Products
        self.product1 = self.env.ref("product.product_product_13")
        self.product2 = self.env.ref("product.product_product_25")

        # Sublocation
        self.shelf2 = self.env.ref("stock.stock_location_14")

        # Purchase Orders
        self.po1 = self.purchase_order_obj.create(
            {
                "partner_id": self.ref("base.res_partner_3"),
            }
        )
        self.po1_line1 = self.purchase_order_line_obj.create(
            {
                "order_id": self.po1.id,
                "product_id": self.product1.id,
                "product_uom": self.product1.uom_id.id,
                "name": self.product1.name,
                "price_unit": self.product1.standard_price,
                "date_planned": fields.datetime.now(),
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
                "date_planned": fields.datetime.now(),
                "product_qty": 12.0,
            }
        )

        self.po2 = self.purchase_order_obj.create(
            {
                "partner_id": self.ref("base.res_partner_3"),
            }
        )
        self.po2_line1 = self.purchase_order_line_obj.create(
            {
                "order_id": self.po2.id,
                "product_id": self.product1.id,
                "product_uom": self.product1.uom_id.id,
                "name": self.product1.name,
                "price_unit": self.product1.standard_price,
                "date_planned": fields.datetime.now(),
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
                "date_planned": fields.datetime.now(),
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
        self.assertTrue(self.po1_line1.pending_to_receive)
        self.assertTrue(self.po1_line2.pending_to_receive)
        self.assertEqual(self.po1_line1.existing_qty, 0)
        self.assertEqual(self.po1_line2.existing_qty, 0)
        self.assertFalse(
            self.po1.picking_ids,
            "Purchase Manual Delivery: no picking should had been created",
        )
        # create a manual delivery for one line (product1)
        wizard = (
            self.env["create.stock.picking.wizard"]
            .with_context(
                **{
                    "active_model": "purchase.order",
                    "active_id": self.po1.id,
                    "active_ids": self.po1.ids,
                }
            )
            .create({})
        )
        wizard.fill_lines(self.po1.order_line)
        wizard.line_ids = wizard.line_ids - wizard.line_ids.filtered(
            lambda l: l.product_id == self.product2
        )
        wizard.create_stock_picking()
        # check picking is created
        self.assertTrue(
            self.po1.picking_ids,
            'Purchase Manual Delivery: picking \
            should be created after "manual delivery" wizard call',
        )
        picking_id = self.po1.picking_ids[0]
        # create a manual delivery, other product (product2)
        wizard = (
            self.env["create.stock.picking.wizard"]
            .with_context(
                **{
                    "active_model": "purchase.order",
                    "active_id": self.po1.id,
                    "active_ids": self.po1.ids,
                }
            )
            .create({})
        )
        wizard.fill_lines(self.po1.order_line)
        self.assertEqual(len(wizard.line_ids), 1)
        self.assertEqual(wizard.line_ids[0].product_id, self.product2)
        wizard.picking_id = picking_id
        wizard.create_stock_picking()
        self.assertEqual(
            len(self.po1.picking_ids),
            1,
            "No extra picking should have been created",
        )
        # create a manual delivery, no lines should be proposed
        wizard = (
            self.env["create.stock.picking.wizard"]
            .with_context(
                **{
                    "active_model": "purchase.order",
                    "active_id": self.po1.id,
                    "active_ids": self.po1.ids,
                }
            )
            .create({})
        )
        wizard.fill_lines(self.po1.order_line)
        self.assertFalse(
            wizard.line_ids,
            "Purchase Manual Delivery: After picking \
            creation for all products, no lines should be left in the wizard",
        )
        self.assertFalse(self.po1_line1.pending_to_receive)
        self.assertFalse(self.po1_line2.pending_to_receive)
        self.assertEqual(self.po1_line1.existing_qty, self.po1_line1.product_qty)
        self.assertEqual(self.po1_line2.existing_qty, self.po1_line2.product_qty)

    def test_02_purchase_order_line_manual_delivery(self):
        """
        Confirm Purchase Order 1 and 2, try to create incoming shipment
        from two PO lines from different PO (error), create one reception
        for two PO lines from same PO twice.
        """
        # confirm RFQ
        self.po1.button_confirm_manual()
        self.po2.button_confirm_manual()
        self.assertTrue(self.po1_line1.pending_to_receive)
        self.assertTrue(self.po1_line2.pending_to_receive)
        self.assertTrue(self.po2_line1.pending_to_receive)
        self.assertTrue(self.po2_line2.pending_to_receive)
        self.assertEqual(self.po1_line1.existing_qty, 0)
        self.assertEqual(self.po1_line2.existing_qty, 0)
        self.assertEqual(self.po2_line1.existing_qty, 0)
        self.assertEqual(self.po2_line2.existing_qty, 0)
        with self.assertRaises(UserError):
            # create a manual delivery for two lines different PO
            self.env["create.stock.picking.wizard"].with_context(
                **{
                    "active_model": "purchase.order.line",
                    "active_ids": [self.po1_line1.id, self.po2_line1.id],
                }
            ).create({})

        # create a manual delivery for lines in PO2
        wizard = (
            self.env["create.stock.picking.wizard"]
            .with_context(
                **{
                    "active_model": "purchase.order.line",
                    "active_ids": self.po2.order_line.ids,
                }
            )
            .create({})
        )
        wizard.fill_lines(self.po2.order_line)
        wizard.create_stock_picking()
        self.assertTrue(
            self.po2.picking_ids,
            'Purchase Manual Delivery: picking \
            should be created after "manual delivery" wizard call',
        )
        self.assertTrue(self.po1_line1.pending_to_receive)
        self.assertTrue(self.po1_line2.pending_to_receive)
        self.assertFalse(self.po2_line1.pending_to_receive)
        self.assertFalse(self.po2_line2.pending_to_receive)
        self.assertEqual(self.po1_line1.existing_qty, 0)
        self.assertEqual(self.po1_line2.existing_qty, 0)
        self.assertEqual(self.po2_line1.existing_qty, self.po2_line1.product_qty)
        self.assertEqual(self.po2_line2.existing_qty, self.po2_line2.product_qty)

    def test_03_purchase_order_line_location(self):
        """
        Confirm Purchase Order 1, create one reception changing the
        location, check location has been correctly set in Picking.
        """
        grp_multi_loc = self.env.ref("stock.group_stock_multi_locations")
        self.env.user.write({"groups_id": [(4, grp_multi_loc.id, 0)]})
        # confirm RFQ
        self.po1.button_confirm_manual()
        self.assertTrue(self.po1_line1.pending_to_receive)
        self.assertTrue(self.po1_line2.pending_to_receive)
        self.assertEqual(self.po1_line1.existing_qty, 0)
        self.assertEqual(self.po1_line2.existing_qty, 0)
        # create a manual delivery for one line (product1)
        wizard = (
            self.env["create.stock.picking.wizard"]
            .with_context(
                **{
                    "active_model": "purchase.order",
                    "active_id": self.po1.id,
                    "active_ids": self.po1.ids,
                }
            )
            .create({})
        )
        wizard.fill_lines(self.po1.order_line)
        wizard.line_ids = wizard.line_ids - wizard.line_ids.filtered(
            lambda l: l.product_id == self.product2
        )
        wizard.location_dest_id = self.shelf2
        wizard.create_stock_picking()
        # check picking is created
        picking_id = self.po1.picking_ids[0]
        self.assertEqual(picking_id.location_dest_id, self.shelf2)
        self.assertFalse(self.po1_line1.pending_to_receive)
        self.assertTrue(self.po1_line2.pending_to_receive)
        self.assertEqual(self.po1_line1.existing_qty, self.po1_line1.product_qty)
        self.assertEqual(self.po1_line2.existing_qty, 0)
