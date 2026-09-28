# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.tests.common import TransactionCase


class TestThreeStepReception(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.wh = cls.env.ref("stock.warehouse0")
        cls.po = cls.env.ref("purchase.purchase_order_2")

    def test_three_steps_generate_three_pickings(self):
        self.wh.reception_steps = "three_steps"
        self.po.button_confirm()
        self.assertEqual(1, self.po.incoming_picking_count)
        self.assertEqual(1, self.po.all_picking_count)
        self.po.all_picking_ids.filtered(
            lambda x: x.state == "assigned"
        ).button_validate()
        self.po._compute_all_pickings()
        self.po._compute_all_picking_count()
        self.assertEqual(2, self.po.all_picking_count)
        self.po.all_picking_ids.filtered(
            lambda x: x.state == "assigned"
        ).button_validate()
        self.po._compute_all_pickings()
        self.po._compute_all_picking_count()
        self.assertEqual(3, self.po.all_picking_count)

    def test_picking_of_other_document_excluded(self):
        self.po.button_confirm()
        other_picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.wh.out_type_id.id,
                "location_id": self.wh.lot_stock_id.id,
                "location_dest_id": self.env.ref("stock.stock_location_customers").id,
                "group_id": self.po.group_id.id,
            }
        )
        self.po._compute_all_pickings()
        self.po._compute_all_picking_count()
        self.assertNotIn(other_picking, self.po.all_picking_ids)
        self.assertEqual(1, self.po.all_picking_count)

    def test_action_view_all_pickings_one_step(self):
        self.po.button_confirm()
        action_data = self.po.action_view_all_pickings()
        form_view = self.env.ref("stock.view_picking_form")
        self.assertEqual(1, self.po.all_picking_count)
        self.assertEqual(
            action_data["views"],
            [(form_view.id, "form")]
            + [
                (state, view)
                for state, view in action_data.get("views", [])
                if view != "form"
            ],
        )
        self.assertEqual(action_data["res_id"], self.po.all_picking_ids.id)

    def test_action_view_all_pickings_three_step(self):
        self.wh.reception_steps = "three_steps"
        self.po.button_confirm()
        action_data = self.po.action_view_all_pickings()
        self.assertEqual([action_data["res_id"]], self.po.all_picking_ids.ids)
        self.po.all_picking_ids.filtered(
            lambda x: x.state == "assigned"
        ).button_validate()
        self.po._compute_all_pickings()
        self.po.all_picking_ids.filtered(
            lambda x: x.state == "assigned"
        ).button_validate()
        self.po._compute_all_pickings()
        action_data = self.po.action_view_all_pickings()
        self.assertEqual(
            action_data["domain"],
            [("id", "in", self.po.all_picking_ids.ids)],
        )
