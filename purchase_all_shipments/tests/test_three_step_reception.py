# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.tests.common import SavepointCase


class TestThreeStepReception(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.wh = cls.env.ref("stock.warehouse0")
        cls.po = cls.env.ref("purchase.purchase_order_1")
        cls.po.location_id = cls.wh.wh_input_stock_loc_id

    def test_three_steps_generate_three_pickings(self):
        self.wh.reception_steps = "three_steps"
        self.po.button_confirm()
        self.assertEqual(1, self.po.picking_count)
        self.assertEqual(3, self.po.all_picking_count)

    def test_action_view_all_pickings_one_step(self):
        self.po.button_confirm()
        action_data = self.po.action_view_all_pickings()
        form_view = self.env.ref("stock.view_picking_form")
        self.assertEqual(1, self.po.all_picking_count)
        self.assertEqual(action_data["views"], [(form_view.id, "form")])
        self.assertEqual(action_data["res_id"], self.po.all_picking_ids.id)

    def test_action_view_all_pickings_three_step(self):
        self.wh.reception_steps = "three_steps"
        self.po.button_confirm()
        action_data = self.po.action_view_all_pickings()
        self.assertEqual(
            action_data["domain"], [("id", "in", self.po.all_picking_ids.ids)],
        )
