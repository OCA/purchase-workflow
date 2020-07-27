# Copyright 2020 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import Form, SavepointCase


class TestPurchaseOrderLinePriceHistoryDiscount(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_1 = cls.env['res.partner'].create({'name': 'Partner 1'})
        cls.product = cls.env['product.product'].create({'name': 'Product 1'})
        # Create a purchase order
        purchase_form = Form(cls.env['purchase.order'])
        purchase_form.partner_id = cls.partner_1
        with purchase_form.order_line.new() as line_form:
            line_form.product_id = cls.product
            line_form.product_qty = 2
            line_form.discount = 10
            line_form.price_unit = 10
        cls.purchase_order_1 = purchase_form.save()
        cls.purchase_order_1.button_confirm()
        # A non-confirmed purchase orders with the same partner and product
        # of cls.purchase_order_1, but different unit price and discount
        purchase_form = Form(cls.env['purchase.order'])
        purchase_form.partner_id = cls.partner_1
        with purchase_form.order_line.new() as line_form:
            line_form.product_id = cls.product
            line_form.product_qty = 2
            line_form.discount = 20
            line_form.price_unit = 20
        cls.purchase_order_2 = purchase_form.save()

    def launch_wizard(self, active_id):
        wizard_obj = self.env['purchase.order.line.price.history']
        wizard = wizard_obj.with_context(active_id=active_id).create({})
        wizard._onchange_partner_id()
        return wizard

    def test_action_set_price(self):
        # Create a wizard from self.purchase_order_2.order_line.
        wizard = self.launch_wizard(self.purchase_order_2.order_line.id)
        self.assertEqual(self.purchase_order_2.order_line.price_unit, 20)
        self.assertEqual(self.purchase_order_2.order_line.discount, 20)
        # Set the price of the history line to the purchase order line.
        wizard.line_ids.action_set_price()
        self.assertEqual(self.purchase_order_2.order_line.price_unit, 10)
        self.assertEqual(self.purchase_order_2.order_line.discount, 10)
