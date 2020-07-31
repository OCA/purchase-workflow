# Copyright 2020 Tecnativa - Ernesto Tejeda
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.purchase_order_line_price_history.tests.test_purchase_order_line_price_history import (  # noqa: B950
    TestPurchaseOrderLinePriceHistoryBase,
)


class TestPurchaseOrderLinePriceHistoryDiscount(TestPurchaseOrderLinePriceHistoryBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.purchase_order_1.order_line.discount = 10
        cls.purchase_order_2.partner_id = cls.partner_1.id
        cls.purchase_order_2.order_line.discount = 20

    def test_action_set_price(self):
        # Create a wizard from self.purchase_order_2.order_line
        wizard = self.launch_wizard(self.purchase_order_2.order_line.id)
        self.assertEqual(wizard.line_ids.discount, 10)
        # Set the price of the history line to the purchase order line
        wizard.line_ids.action_set_price()
        self.assertEqual(self.purchase_order_2.order_line.price_unit, 10)
        self.assertEqual(self.purchase_order_2.order_line.discount, 10)
