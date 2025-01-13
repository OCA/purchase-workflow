# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests import Form, common
from odoo.tools import mute_logger


class TestPurchaseServicePicking(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                mail_create_nolog=True,
                mail_create_nosubscribe=True,
                mail_notrack=True,
                no_reset_password=True,
                tracking_disable=True,
            )
        )
        cls.partner = cls.env["res.partner"].create({"name": "Mr Odoo"})
        cls.service_product = cls.env["product.product"].create(
            {
                "name": "Test service product",
                "type": "service",
            }
        )
        cls.consu_product = cls.env["product.product"].create(
            {
                "name": "Test consu product",
                "type": "consu",
            }
        )
        cls.order = cls._create_order()

    @classmethod
    def _create_order(cls):
        order_form = Form(cls.env["purchase.order"])
        order_form.partner_id = cls.partner
        with order_form.order_line.new() as line_form:
            line_form.product_id = cls.service_product
            line_form.product_qty = 2
        return order_form.save()

    def test_purchase_sevice_flow_with_consu_product(self):
        """Order with consu product"""
        self.order.order_line.product_id = self.consu_product
        self.order.button_confirm()
        self.assertFalse(self.order.service_picking_ids)

    def test_purchase_sevice_flow_cancel_order(self):
        """Order confirmed + cancelled"""
        self.order.button_confirm()
        self.assertTrue(self.order.service_picking_ids)
        self.assertEqual(self.order.service_picking_ids.state, "in_progress")
        self.order.button_cancel()
        self.assertEqual(self.order.service_picking_ids.state, "cancel")

    def test_purchase_sevice_flow_manual_quantity_done(self):
        """Order with service product"""
        self.order.button_confirm()
        self.assertTrue(self.order.service_picking_ids)
        picking = self.order.service_picking_ids
        self.assertIn("SP/", picking.name)
        self.assertEqual(picking.state, "in_progress")
        self.assertEqual(picking.partner_id, self.partner)
        self.assertFalse(picking.user_id)
        self.assertEqual(picking.date, self.order.date_order)
        self.assertEqual(picking.origin, self.order.name)
        self.assertEqual(picking.purchase_id, self.order)
        self.assertEqual(len(picking.line_ids), 1)
        self.assertEqual(picking.line_ids.product_id, self.service_product)
        self.assertEqual(picking.line_ids.product_uom_qty, 2)
        self.assertEqual(picking.line_ids.quantity_done, 0)
        # Set quantity_done
        picking.line_ids.quantity_done = 2
        picking.action_validate()
        self.assertEqual(picking.state, "done")
        self.assertEqual(self.order.order_line.qty_received, 2)
        with self.assertRaises(UserError):
            self.order.button_cancel()

    def test_purchase_sevice_flow_cancel(self):
        """Order with consu + service products + cancel process"""
        service_line = self.order.order_line
        order_form = Form(self.order)
        with order_form.order_line.new() as line_form:
            line_form.product_id = self.consu_product
        self.order = order_form.save()
        consu_line = self.order.order_line - service_line
        self.order.button_confirm()
        self.assertTrue(self.order.service_picking_ids)
        picking = self.order.service_picking_ids
        self.assertEqual(picking.state, "in_progress")
        self.assertEqual(len(picking.line_ids), 1)
        self.assertEqual(picking.line_ids.product_id, self.service_product)
        self.assertTrue(service_line.service_picking_line_ids)
        self.assertFalse(consu_line.service_picking_line_ids)
        picking.action_cancel()
        self.assertEqual(picking.state, "cancel")
        self.assertEqual(service_line.qty_received, 0)

    def test_purchase_sevice_flow_immediate_transfer(self):
        """Inmediate transfer process"""
        self.order.button_confirm()
        picking = self.order.service_picking_ids
        res = picking.action_validate()
        self.assertEqual(res["res_model"], "service.immediate.transfer")
        wizard = self.env[res["res_model"]].with_context(res["context"]).create({})
        self.assertEqual(len(wizard.line_ids), 1)
        self.assertEqual(wizard.line_ids.picking_id, picking)
        self.assertTrue(wizard.line_ids.to_immediate)
        wizard.process()
        self.assertEqual(picking.state, "done")
        self.assertEqual(picking.line_ids.quantity_done, 2)
        self.assertEqual(self.order.order_line.qty_received, 2)

    def test_purchase_sevice_flow_backorder_01(self):
        """Backorder process"""
        self.order.button_confirm()
        picking = self.order.service_picking_ids
        picking.line_ids.quantity_done = 1
        picking = self.order.service_picking_ids
        res = picking.action_validate()
        self.assertEqual(res["res_model"], "service.backorder.confirmation")
        wizard = self.env[res["res_model"]].with_context(res["context"]).create({})
        self.assertEqual(len(wizard.line_ids), 1)
        self.assertEqual(wizard.line_ids.picking_id, picking)
        self.assertTrue(wizard.line_ids.to_backorder)
        wizard.process()
        self.assertEqual(picking.state, "done")
        self.assertEqual(picking.line_ids.product_uom_qty, 1)
        self.assertEqual(picking.line_ids.quantity_done, 1)
        self.assertEqual(self.order.order_line.qty_received, 1)
        self.assertTrue(picking.backorder_ids)
        backorder = picking.backorder_ids
        self.assertEqual(backorder.backorder_id, picking)
        self.assertEqual(backorder.state, "in_progress")
        self.assertEqual(len(backorder.line_ids), 1)
        self.assertEqual(backorder.line_ids.product_uom_qty, 1)
        self.assertEqual(backorder.line_ids.quantity_done, 0)
        # Set quantity_done
        backorder.line_ids.quantity_done = 1
        backorder.action_validate()
        self.assertEqual(self.order.order_line.qty_received, 2)

    def test_purchase_sevice_flow_backorder_02(self):
        """Cancel backorder process"""
        self.order.button_confirm()
        picking = self.order.service_picking_ids
        picking.line_ids.quantity_done = 1
        picking = self.order.service_picking_ids
        res = picking.action_validate()
        self.assertEqual(res["res_model"], "service.backorder.confirmation")
        wizard = self.env[res["res_model"]].with_context(res["context"]).create({})
        self.assertEqual(len(wizard.line_ids), 1)
        self.assertEqual(wizard.line_ids.picking_id, picking)
        self.assertTrue(wizard.line_ids.to_backorder)
        wizard.process_cancel_backorder()
        self.assertEqual(picking.state, "done")
        self.assertEqual(picking.line_ids.product_uom_qty, 1)
        self.assertEqual(picking.line_ids.quantity_done, 1)
        self.assertEqual(self.order.order_line.qty_received, 1)
        self.assertFalse(picking.backorder_ids)

    def test_purchase_sevice_flow_backorder_03(self):
        """Backorder process + reduce order line quantity"""
        line = self.order.order_line
        line.write({"product_qty": 3})
        self.order.button_confirm()
        picking = self.order.service_picking_ids
        picking.line_ids.quantity_done = 1
        picking = self.order.service_picking_ids
        res = picking.action_validate()
        self.assertEqual(res["res_model"], "service.backorder.confirmation")
        wizard = self.env[res["res_model"]].with_context(res["context"]).create({})
        self.assertEqual(len(wizard.line_ids), 1)
        self.assertEqual(wizard.line_ids.picking_id, picking)
        self.assertTrue(wizard.line_ids.to_backorder)
        wizard.process()
        self.assertTrue(picking.backorder_ids)
        backorder = picking.backorder_ids
        self.assertEqual(backorder.backorder_id, picking)
        self.assertEqual(backorder.state, "in_progress")
        self.assertEqual(len(backorder.line_ids), 1)
        self.assertEqual(backorder.line_ids.product_uom_qty, 2)
        self.assertEqual(backorder.line_ids.quantity_done, 0)
        line.write({"product_qty": 1})
        self.assertEqual(backorder.state, "cancel")
        self.assertEqual(backorder.line_ids.product_uom_qty, 0)

    def test_purchase_sevice_flow_backorder_04(self):
        """Backorder process + reduce order line quantity (error)"""
        line = self.order.order_line
        line.write({"product_qty": 3})
        self.order.button_confirm()
        picking = self.order.service_picking_ids
        picking.line_ids.quantity_done = 2
        picking = self.order.service_picking_ids
        res = picking.action_validate()
        self.assertEqual(res["res_model"], "service.backorder.confirmation")
        wizard = self.env[res["res_model"]].with_context(res["context"]).create({})
        self.assertEqual(len(wizard.line_ids), 1)
        self.assertEqual(wizard.line_ids.picking_id, picking)
        self.assertTrue(wizard.line_ids.to_backorder)
        wizard.process()
        self.assertTrue(picking.backorder_ids)
        backorder = picking.backorder_ids
        self.assertEqual(backorder.backorder_id, picking)
        self.assertEqual(backorder.state, "in_progress")
        self.assertEqual(len(backorder.line_ids), 1)
        self.assertEqual(backorder.line_ids.product_uom_qty, 1)
        self.assertEqual(backorder.line_ids.quantity_done, 0)
        with self.assertRaises(UserError):
            line.write({"product_qty": 1})

    @mute_logger("odoo.models.unlink")
    def test_purchase_sevice_flow_pol_update_01(self):
        """Modify line quantity when order is already confirmed."""
        order_line = self.order.order_line
        self.order.button_confirm()
        picking = self.order.service_picking_ids
        self.assertEqual(len(picking.line_ids), 1)
        picking_line = picking.line_ids
        self.assertEqual(picking_line.product_uom_qty, 2)
        order_line.write({"product_qty": 3})
        self.assertEqual(len(picking.line_ids), 1)
        self.assertEqual(picking_line.product_uom_qty, 3)
        order_line.write({"product_qty": 1})
        self.assertEqual(len(picking.line_ids), 1)
        self.assertEqual(picking_line.product_uom_qty, 1)
        order_form = Form(
            self.order.with_context(default_product_id=self.service_product.id)
        )
        with order_form.order_line.new() as line_form:
            line_form.product_qty = 2
        order_form.save()
        order_line_extra = self.order.order_line - order_line
        self.assertEqual(len(picking.line_ids), 2)
        picking_line_extra = picking.line_ids - picking_line
        self.assertEqual(picking_line.product_uom_qty, 1)
        self.assertEqual(picking_line_extra.product_uom_qty, 2)
        picking_line.quantity_done = 1
        picking_line_extra.quantity_done = 2
        picking.action_validate()
        self.assertEqual(picking.state, "done")
        self.assertEqual(order_line.qty_received, 1)
        self.assertEqual(order_line_extra.qty_received, 2)

    def test_purchase_sevice_flow_pol_update_02(self):
        """Modify (reduce) line quantity when picking is done."""
        order_line = self.order.order_line
        self.order.button_confirm()
        picking = self.order.service_picking_ids
        picking.line_ids.quantity_done = 2
        picking.action_validate()
        self.assertEqual(picking.state, "done")
        self.assertEqual(order_line.qty_received, 2)
        with self.assertRaises(UserError):
            order_line.write({"product_qty": 1})

    def test_purchase_sevice_flow_pol_extra(self):
        """Validate picking + extra picking."""
        order_line = self.order.order_line
        self.order.button_confirm()
        picking = self.order.service_picking_ids
        self.assertEqual(len(picking.line_ids), 1)
        self.assertEqual(picking.line_ids.product_uom_qty, 2)
        picking.line_ids.quantity_done = 2
        picking.action_validate()
        self.assertEqual(picking.state, "done")
        self.assertEqual(order_line.qty_received, 2)
        order_form = Form(
            self.order.with_context(default_product_id=self.service_product.id)
        )
        with order_form.order_line.new() as line_form:
            line_form.product_qty = 1
        order_form.save()
        order_line_extra = self.order.order_line - order_line
        picking_exta = self.order.service_picking_ids - picking
        self.assertEqual(len(self.order.service_picking_ids), 2)
        self.assertEqual(picking_exta.state, "in_progress")
        self.assertEqual(len(picking_exta.line_ids), 1)
        self.assertEqual(picking_exta.line_ids.product_uom_qty, 1)
        picking_exta.line_ids.quantity_done = 1
        picking_exta.action_validate()
        self.assertEqual(picking_exta.state, "done")
        self.assertEqual(order_line_extra.qty_received, 1)

    def _create_return_picking(self, picking):
        wizard_return_form = Form(
            self.env["service.return.picking"].with_context(
                active_id=picking.id, active_ids=picking.ids, active_model=picking._name
            )
        )
        return wizard_return_form.save()

    def test_purchase_sevice_flow_return_error_01(self):
        """Error return picking (qty 0)"""
        self.order.button_confirm()
        picking = self.order.service_picking_ids
        self.assertEqual(len(picking.line_ids), 1)
        self.assertEqual(picking.line_ids.product_uom_qty, 2)
        picking.line_ids.quantity_done = 2
        picking.action_validate()
        self.assertEqual(picking.state, "done")
        self.assertEqual(self.order.order_line.qty_received, 2)
        wizard_return = self._create_return_picking(picking)
        self.assertTrue(wizard_return.product_return_lines)
        wizard_return.product_return_lines.quantity = 0
        with self.assertRaises(UserError):
            wizard_return.create_returns()

    def test_purchase_sevice_flow_return_error_02(self):
        """Error return picking (higher qty)"""
        self.order.button_confirm()
        picking = self.order.service_picking_ids
        self.assertEqual(len(picking.line_ids), 1)
        self.assertEqual(picking.line_ids.product_uom_qty, 2)
        picking.line_ids.quantity_done = 2
        picking.action_validate()
        self.assertEqual(picking.state, "done")
        self.assertEqual(self.order.order_line.qty_received, 2)
        wizard_return = self._create_return_picking(picking)
        self.assertTrue(wizard_return.product_return_lines)
        wizard_return.product_return_lines.quantity = 3
        with self.assertRaises(UserError):
            wizard_return.create_returns()

    def test_purchase_sevice_flow_return_01(self):
        """Full return picking"""
        self.order.button_confirm()
        picking = self.order.service_picking_ids
        self.assertEqual(len(picking.line_ids), 1)
        self.assertEqual(picking.line_ids.product_uom_qty, 2)
        picking.line_ids.quantity_done = 2
        picking.action_validate()
        self.assertEqual(picking.state, "done")
        self.assertEqual(self.order.order_line.qty_received, 2)
        wizard_return = self._create_return_picking(picking)
        res = wizard_return.create_returns()
        self.assertEqual(res["res_model"], "service.picking")
        return_picking = self.env[res["res_model"]].browse(res["res_id"])
        self.assertIn("SPR/", return_picking.name)
        self.assertEqual(len(return_picking.line_ids), 1)
        self.assertEqual(return_picking.line_ids.product_id, self.service_product)
        self.assertEqual(return_picking.line_ids.product_uom_qty, 2)
        self.assertEqual(return_picking.line_ids.quantity_done, 0)
        self.assertEqual(
            return_picking.line_ids.origin_returned_line_id, picking.line_ids
        )
        return_picking.line_ids.quantity_done = 2
        return_picking.action_validate()
        self.assertEqual(self.order.order_line.qty_received, 0)

    def test_purchase_sevice_flow_return_02(self):
        """Partial return picking"""
        self.order.button_confirm()
        picking = self.order.service_picking_ids
        self.assertEqual(len(picking.line_ids), 1)
        self.assertEqual(picking.line_ids.product_uom_qty, 2)
        picking.line_ids.quantity_done = 2
        picking.action_validate()
        self.assertEqual(picking.state, "done")
        self.assertEqual(self.order.order_line.qty_received, 2)
        wizard_return = self._create_return_picking(picking)
        wizard_return.product_return_lines.quantity = 1
        res = wizard_return.create_returns()
        self.assertEqual(res["res_model"], "service.picking")
        return_picking = self.env[res["res_model"]].browse(res["res_id"])
        self.assertIn("SPR/", return_picking.name)
        self.assertEqual(len(return_picking.line_ids), 1)
        self.assertEqual(return_picking.line_ids.product_id, self.service_product)
        self.assertEqual(return_picking.line_ids.product_uom_qty, 1)
        self.assertEqual(return_picking.line_ids.quantity_done, 0)
        self.assertEqual(
            return_picking.line_ids.origin_returned_line_id, picking.line_ids
        )
        return_picking.line_ids.quantity_done = 1
        return_picking.action_validate()
        self.assertEqual(self.order.order_line.qty_received, 1)
