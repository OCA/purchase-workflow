# Copyright 2019 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import Form, TransactionCase

from odoo.addons.mail.tests.common import mail_new_test_user


class TestPurchaseManualDelivery(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.purchase_order_obj = cls.env["purchase.order"]
        cls.purchase_order_line_obj = cls.env["purchase.order.line"]
        cls.stock_picking_obj = cls.env["stock.picking"]
        cls.env.company.purchase_manual_delivery = True
        # Products
        cls.product1 = cls.env.ref("product.product_product_13")
        cls.product2 = cls.env.ref("product.product_product_25")

        # Sublocation
        cls.shelf2 = cls.env.ref("stock.stock_location_14")

        # Purchase Orders
        cls.po1 = cls.purchase_order_obj.create(
            {
                "partner_id": cls.env.ref("base.res_partner_3").id,
            }
        )
        cls.po1_line1 = cls.purchase_order_line_obj.create(
            {
                "order_id": cls.po1.id,
                "product_id": cls.product1.id,
                "product_uom": cls.product1.uom_id.id,
                "name": cls.product1.name,
                "price_unit": cls.product1.standard_price,
                "date_planned": fields.datetime.now(),
                "product_qty": 42.0,
            }
        )
        cls.po1_line2 = cls.purchase_order_line_obj.create(
            {
                "order_id": cls.po1.id,
                "product_id": cls.product2.id,
                "product_uom": cls.product2.uom_id.id,
                "name": cls.product2.name,
                "price_unit": cls.product2.standard_price,
                "date_planned": fields.datetime.now(),
                "product_qty": 12.0,
            }
        )

        cls.po2 = cls.purchase_order_obj.create(
            {
                "partner_id": cls.env.ref("base.res_partner_3").id,
            }
        )
        cls.po2_line1 = cls.purchase_order_line_obj.create(
            {
                "order_id": cls.po2.id,
                "product_id": cls.product1.id,
                "product_uom": cls.product1.uom_id.id,
                "name": cls.product1.name,
                "price_unit": cls.product1.standard_price,
                "date_planned": fields.datetime.now(),
                "product_qty": 10.0,
            }
        )
        cls.po2_line2 = cls.purchase_order_line_obj.create(
            {
                "order_id": cls.po2.id,
                "product_id": cls.product2.id,
                "product_uom": cls.product2.uom_id.id,
                "name": cls.product2.name,
                "price_unit": cls.product2.standard_price,
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
        self.po1.button_confirm()
        self.assertTrue(self.po1_line1.pending_to_receive)
        self.assertTrue(self.po1_line2.pending_to_receive)
        self.assertEqual(self.po1_line1.qty_in_receipt, 0)
        self.assertEqual(self.po1_line2.qty_in_receipt, 0)
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
            lambda li: li.product_id == self.product2
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

        # The quantity is checked against the remaining quantity of the line
        with self.assertRaisesRegex(
            UserError,
            "more than the remaining quantity",
        ):
            with self.env.cr.savepoint():
                wizard.line_ids.qty += 1
                wizard.create_stock_picking()

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
        self.assertEqual(self.po1_line1.qty_in_receipt, self.po1_line1.product_qty)
        self.assertEqual(self.po1_line2.qty_in_receipt, self.po1_line2.product_qty)
        self.assertFalse(self.po1.pending_to_receive)

        # Process the picking
        picking = self.po1.picking_ids
        for move in picking.move_ids:
            move.quantity = move.product_qty
        picking.button_validate()

        # Process some returns
        stock_return_picking_form = Form(
            self.env["stock.return.picking"].with_context(
                active_ids=picking.ids,
                active_id=picking.id,
                active_model=picking._name,
            )
        )
        return_wiz = stock_return_picking_form.save()
        return_wiz.product_return_moves.filtered(
            lambda prm: prm.move_id.purchase_line_id == self.po1_line1
        ).write(
            {
                "quantity": 2,
                "to_refund": True,
            }
        )
        return_wiz.product_return_moves.filtered(
            lambda prm: prm.move_id.purchase_line_id == self.po1_line2
        ).write(
            {
                "quantity": 2,
                "to_refund": False,
            }
        )
        return_wiz.action_create_returns()

        # The refund line is open to re-receive the returned item
        self.assertTrue(self.po1_line1.pending_to_receive)
        self.assertEqual(self.po1_line1.qty_in_receipt, -2)
        # But the non-refund line is not
        self.assertFalse(self.po1_line2.qty_in_receipt)
        self.assertFalse(self.po1_line2.pending_to_receive)

        self.assertTrue(self.po1.pending_to_receive)

    def test_02_purchase_order_line_manual_delivery(self):
        """
        Confirm Purchase Order 1 and 2, try to create incoming shipment
        from two PO lines from different PO (error), create one reception
        for two PO lines from same PO twice.
        """
        # confirm RFQ
        self.po1.button_confirm()
        self.po2.button_confirm()
        self.assertTrue(self.po1_line1.pending_to_receive)
        self.assertTrue(self.po1_line2.pending_to_receive)
        self.assertTrue(self.po2_line1.pending_to_receive)
        self.assertTrue(self.po2_line2.pending_to_receive)
        self.assertEqual(self.po1_line1.qty_in_receipt, 0)
        self.assertEqual(self.po1_line2.qty_in_receipt, 0)
        self.assertEqual(self.po2_line1.qty_in_receipt, 0)
        self.assertEqual(self.po2_line2.qty_in_receipt, 0)
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
        self.assertEqual(self.po1_line1.qty_in_receipt, 0)
        self.assertEqual(self.po1_line2.qty_in_receipt, 0)
        self.assertEqual(self.po2_line1.qty_in_receipt, self.po2_line1.product_qty)
        self.assertEqual(self.po2_line2.qty_in_receipt, self.po2_line2.product_qty)

    def test_03_purchase_order_line_location(self):
        """
        Confirm Purchase Order 1, create one reception changing the
        location, check location has been correctly set in Picking.
        """
        grp_multi_loc = self.env.ref("stock.group_stock_multi_locations")
        self.env.user.write({"groups_id": [(4, grp_multi_loc.id, 0)]})
        # confirm RFQ
        self.po1.button_confirm()
        self.assertTrue(self.po1_line1.pending_to_receive)
        self.assertTrue(self.po1_line2.pending_to_receive)
        self.assertEqual(self.po1_line1.qty_in_receipt, 0)
        self.assertEqual(self.po1_line2.qty_in_receipt, 0)
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
            lambda li: li.product_id == self.product2
        )
        wizard.location_dest_id = self.shelf2
        wizard.create_stock_picking()
        # check picking is created
        picking_id = self.po1.picking_ids[0]
        self.assertEqual(picking_id.location_dest_id, self.shelf2)
        self.assertFalse(self.po1_line1.pending_to_receive)
        self.assertTrue(self.po1_line2.pending_to_receive)
        self.assertEqual(self.po1_line1.qty_in_receipt, self.po1_line1.product_qty)
        self.assertEqual(self.po1_line2.qty_in_receipt, 0)

    def test_04_pending_to_receive(self):
        """
        Checks if a purchase order line with existing quantity higher than
        total quantity is not pending to receive
        """
        # Create PO and PO Line
        po_existing_bigger = self.purchase_order_obj.create(
            {
                "partner_id": self.ref("base.res_partner_3"),
            }
        )
        pol_existing_bigger = self.purchase_order_line_obj.create(
            {
                "order_id": po_existing_bigger.id,
                "product_id": self.product1.id,
                "product_uom": self.product1.uom_id.id,
                "name": self.product1.name,
                "price_unit": self.product1.standard_price,
                "date_planned": fields.datetime.now(),
                "product_qty": 5.0,
            }
        )
        po_existing_bigger.button_confirm()
        # create a manual delivery for line in po_existing_bigger
        wizard = (
            self.env["create.stock.picking.wizard"]
            .with_context(
                **{
                    "active_model": "purchase.order.line",
                    "active_ids": po_existing_bigger.order_line.ids,
                }
            )
            .create({})
        )
        wizard.fill_lines(po_existing_bigger.order_line)
        wizard.line_ids.filtered(
            lambda li: li.purchase_order_line_id.id == pol_existing_bigger.id
        ).qty = 1
        wizard.create_stock_picking()

        # Change the done quantity to be bigger than the total needed
        picking_id = po_existing_bigger.picking_ids[0]
        picking_id.move_ids[0].quantity = 6
        picking_id.button_validate()

        # The PO Line should not be pending to receive
        self.assertFalse(po_existing_bigger.pending_to_receive)

    def test_05_purchase_order_in_progress(self):
        """
        Create a new Product and Purchase Order.
        Confirm Purchase Order and create a Picking with only a partial amount of
        the selected amount of the Purchase Order Line. Confirm the Picking.
        The quantity in progress is the pending to receive quantity of the Purchase
        Order Line.
        """
        product_in_progress = self.env["product.product"].create(
            {
                "name": "Test product pending",
                "type": "consu",
                "is_storable": True,
                "list_price": 1,
                "standard_price": 1,
            }
        )
        po_in_progress = self.purchase_order_obj.create(
            {
                "partner_id": self.ref("base.res_partner_3"),
            }
        )
        self.purchase_order_line_obj.create(
            {
                "order_id": po_in_progress.id,
                "product_id": product_in_progress.id,
                "product_uom": product_in_progress.uom_id.id,
                "name": product_in_progress.name,
                "price_unit": product_in_progress.standard_price,
                "date_planned": fields.datetime.now(),
                "product_qty": 5.0,
            }
        )
        po_in_progress.button_confirm()
        location = self.env["stock.location"].browse(
            po_in_progress.picking_type_id.default_location_dest_id.id
        )
        wizard = (
            self.env["create.stock.picking.wizard"]
            .with_context(
                **{
                    "active_model": "purchase.order",
                    "active_id": po_in_progress.id,
                    "active_ids": po_in_progress.ids,
                }
            )
            .create({})
        )
        wizard.fill_lines(po_in_progress.order_line)
        wizard.line_ids[0].qty = 2
        wizard.create_stock_picking()
        po_in_progress.picking_ids[0].button_validate()

        self.assertEqual(po_in_progress.order_line.qty_received, 2)
        self.assertEqual(po_in_progress.order_line.qty_in_receipt, 0)
        self.assertTrue(po_in_progress.order_line.pending_to_receive)

        qty, _ = product_in_progress._get_quantity_in_progress(
            location_ids=location.ids
        )
        self.assertEqual(qty.get((product_in_progress.id, location.id)), 3)

        wizard.line_ids[0].qty = 3
        wizard.create_stock_picking()
        self.assertEqual(po_in_progress.order_line.qty_received, 2)
        self.assertEqual(po_in_progress.order_line.qty_in_receipt, 3)
        self.assertFalse(po_in_progress.order_line.pending_to_receive)

    def test_06_purchase_order_manual_delivery_double_validation(self):
        """
        Confirm Purchase Order 1, check no incoming shipments have been
        pre-created. Approve Purchase Order 1, check no incoming shipments
        have been pre-created.
        """
        self.user_purchase_user = mail_new_test_user(
            self.env,
            name="Pauline Poivraisselle",
            login="pauline",
            email="pur@example.com",
            notification_type="inbox",
            groups="purchase.group_purchase_user",
        )

        # make double validation two step
        self.env.company.write(
            {"po_double_validation": "two_step", "po_double_validation_amount": 2000.00}
        )

        # Create draft RFQ
        po_vals = {
            "partner_id": self.ref("base.res_partner_3"),
            "order_line": [
                (
                    0,
                    0,
                    {
                        "name": self.product1.name,
                        "product_id": self.product1.id,
                        "product_qty": 5.0,
                        "product_uom": self.product1.uom_po_id.id,
                        "price_unit": 5000000.0,
                    },
                )
            ],
        }
        self.po = (
            self.env["purchase.order"]
            .with_user(self.user_purchase_user)
            .create(po_vals)
        )

        # confirm RFQ
        self.po.button_confirm()
        self.assertTrue(self.po.order_line.pending_to_receive)
        self.assertEqual(self.po.order_line.qty_in_receipt, 0)
        self.assertFalse(
            self.po.picking_ids,
            "Purchase Manual Delivery: no picking should had been created",
        )
        self.assertEqual(self.po.state, "to approve")

        # PO approved by manager
        self.po.env.user.groups_id += self.env.ref("purchase.group_purchase_manager")
        self.po.button_approve()
        self.assertTrue(self.po.order_line.pending_to_receive)
        self.assertEqual(self.po.order_line.qty_in_receipt, 0)
        self.assertFalse(
            self.po.picking_ids,
            "Purchase Manual Delivery: no picking should had been created",
        )
        self.assertEqual(self.po.state, "purchase")

    def test_07_purchase_order_ignore_manual_delivery(self):
        """Manual delivery can be overridden with a context key during confirmation"""
        self.po1.with_context(ignore_manual_delivery=True).button_confirm()
        self.assertTrue(
            self.po1.picking_ids,
            "Context key failed to trigger picking creation",
        )
        self.assertTrue(
            self.po1.picking_ids.move_ids,
            "Context key failed to trigger stock move creation",
        )
        for line in self.po1.order_line:
            self.assertFalse(
                line.pending_to_receive,
                "Context key did not create stock moves for all quantities",
            )

    def test_08_purchase_order_line_increase_quantity(self):
        """Increasing the quantity on a confirmed line does not trigger delivery"""
        self.po1.button_confirm()
        self.assertFalse(self.po1.picking_ids)
        self.po1.order_line[0].product_qty += 1
        self.assertFalse(
            self.po1.picking_ids,
            "Increasing the quantity on a confirmed line should not create deliveries",
        )
        # Same on line creation
        self.po1.order_line[0].copy()
        self.assertFalse(self.po1.picking_ids)
        self.assertFalse(
            self.po1.picking_ids,
            "Adding a line to a confirmed order should not create a delivery",
        )
        # Context key forces the delivery
        self.po1.order_line[0].with_context(
            ignore_manual_delivery=True
        ).product_qty += 1
        self.assertTrue(
            self.po1.picking_ids,
            "Passing context key when increasing the quantity on a confirmed line did "
            "not create a delivery",
        )
