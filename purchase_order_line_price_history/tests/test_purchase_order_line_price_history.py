# Copyright 2020 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import Form, SavepointCase


class TestPurchaseOrderLinePriceHistoryBase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_1 = cls.env["res.partner"].create({"name": "Partner 1"})
        cls.partner_2 = cls.env["res.partner"].create({"name": "Partner 2"})
        cls.product = cls.env["product.product"].create({"name": "Product 1"})
        # Two confirmed purchase orders with the same data and
        # different partners
        purchase_form = Form(cls.env["purchase.order"])
        purchase_form.partner_id = cls.partner_1
        with purchase_form.order_line.new() as line_form:
            line_form.product_id = cls.product
            line_form.product_qty = 2
            line_form.price_unit = 10
        cls.purchase_order_1 = purchase_form.save()
        cls.purchase_order_1.button_confirm()
        purchase_form = Form(cls.env["purchase.order"])
        purchase_form.partner_id = cls.partner_2
        with purchase_form.order_line.new() as line_form:
            line_form.product_id = cls.product
            line_form.product_qty = 2
            line_form.price_unit = 20
        cls.purchase_order_2 = purchase_form.save()
        # A non-confirmed purchase orders with the same partner
        # of cls.purchase_order_2
        purchase_form = Form(cls.env["purchase.order"])
        purchase_form.partner_id = cls.partner_2
        with purchase_form.order_line.new() as line_form:
            line_form.product_id = cls.product
            line_form.product_qty = 2
            line_form.price_unit = 30
        cls.purchase_order_3 = purchase_form.save()

    def launch_wizard(self, active_id):
        wizard_obj = self.env["purchase.order.line.price.history"]
        wizard = wizard_obj.with_context(active_id=active_id).create({})
        wizard._onchange_partner_id()
        return wizard


class TestPurchaseOrderLinePriceHistory(TestPurchaseOrderLinePriceHistoryBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.purchase_order_2.button_confirm()

    def test_onchange_partner_id(self):
        # Create a wizard from self.purchase_order_3 order line.
        # Only one history line should be shown and should be
        # associated with self.purchase_order_2 order line
        wizard = self.launch_wizard(self.purchase_order_3.order_line.id)
        self.assertEqual(len(wizard.line_ids), 1)
        self.assertEqual(
            wizard.line_ids.purchase_order_line_id, self.purchase_order_2.order_line,
        )
        self.assertEqual(wizard.line_ids.price_unit, 20)
        # Set partner to False. Two history lines should be shown and
        # they should be associated with self.purchase_order_1 order line
        # and self.purchase_order_2 order line
        wizard.partner_id = False
        wizard._onchange_partner_id()
        self.assertEqual(len(wizard.line_ids), 2)
        self.assertEqual(
            set(wizard.line_ids.mapped("purchase_order_line_id.price_unit")),
            set(list([10.0, 20.0])),
        )

    def test_onchange_partner_id_include_rfq(self):
        # Another purchase orders with the same partner of cls.purchase_order_2
        # and cls.purchase_order_3
        purchase_form = Form(self.env["purchase.order"])
        purchase_form.partner_id = self.partner_2
        with purchase_form.order_line.new() as line_form:
            line_form.product_id = self.product
            line_form.product_qty = 2
            line_form.price_unit = 40
        self.purchase_order_4 = purchase_form.save()
        # Create a wizard from self.purchase_order_4 order line.
        # Only one history line should be shown and should be
        # associated with self.purchase_order_2 order line
        wizard = self.launch_wizard(self.purchase_order_4.order_line.id)
        self.assertEqual(len(wizard.line_ids), 1)
        self.assertEqual(
            wizard.line_ids.purchase_order_line_id, self.purchase_order_2.order_line,
        )
        # If include_rfq is checked two history lines should be shown
        # and they should be associated with self.purchase_order_2 order line
        # and self.purchase_order_3 order line
        wizard.include_rfq = True
        wizard._onchange_partner_id()
        self.assertEqual(len(wizard.line_ids), 2)
        self.assertEqual(
            wizard.line_ids.mapped("purchase_order_line_id"),
            (self.purchase_order_2.order_line | self.purchase_order_3.order_line),
        )

    def test_onchange_partner_id_include_commercial_partner(self):
        # Another purchase orders with a partner child of cls.purchase_order_2
        partner_2_child = self.env["res.partner"].create(
            {"name": "Child of Partner 2", "parent_id": self.partner_2.id},
        )
        purchase_form = Form(self.env["purchase.order"])
        purchase_form.partner_id = partner_2_child
        with purchase_form.order_line.new() as line_form:
            line_form.product_id = self.product
            line_form.product_qty = 2
            line_form.price_unit = 40
        self.purchase_order_4 = purchase_form.save()
        # Create a wizard from self.purchase_order_4 order line. As
        # include_commercial_partner is checked by default, one history line
        # should be shown and associated with self.purchase_order_2 order line
        wizard = self.launch_wizard(self.purchase_order_4.order_line.id)
        self.assertEqual(len(wizard.line_ids), 1)
        self.assertEqual(
            wizard.line_ids.purchase_order_line_id, self.purchase_order_2.order_line,
        )
        # Uncheck include_commercial_partner and purchase history
        # will be empty.
        wizard.include_commercial_partner = False
        wizard._onchange_partner_id()
        self.assertFalse(wizard.line_ids)

    def test_action_set_price(self):
        # Create a wizard from self.purchase_order_3.order_line.
        wizard = self.launch_wizard(self.purchase_order_3.order_line.id)
        self.assertEqual(self.purchase_order_3.order_line.price_unit, 30)
        # Set the price of the history line to the purchase order line.
        wizard.line_ids.action_set_price()
        self.assertEqual(self.purchase_order_3.order_line.price_unit, 20)
        # Create a wizard from self.purchase_order_3 order line again.
        wizard = self.launch_wizard(self.purchase_order_3.order_line.id)
        wizard.partner_id = False
        wizard._onchange_partner_id()
        # Find the history line with price_unit == 10 and set this price
        # to the purchase order line
        history_line = wizard.line_ids.filtered(lambda r: r.price_unit == 10)
        self.assertEqual(self.purchase_order_3.order_line.price_unit, 20)
        history_line.action_set_price()
        self.assertEqual(self.purchase_order_3.order_line.price_unit, 10)
