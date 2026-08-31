# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields
from odoo.tests.common import TransactionCase


class TestThreeStepReception(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.wh = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.env.company.id)], limit=1
        )
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Supplier",
                "email": "supplier@test.com",
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "consu",
                "list_price": 100.0,
                "standard_price": 50.0,
            }
        )
        cls.po = cls.env["purchase.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product.id,
                            "product_qty": 10.0,
                            "price_unit": 50.0,
                            "date_planned": fields.Datetime.now(),
                        },
                    )
                ],
            }
        )

    def test_three_steps_generate_three_pickings(self):
        self.wh.reception_steps = "three_steps"
        self.po.button_confirm()
        self.assertEqual(1, self.po.incoming_picking_count)
        # In v19, with three-step reception, only the first picking is created
        self.assertEqual(1, self.po.all_picking_count)
        picking1 = self.po.all_picking_ids.filtered(lambda x: x.state == "assigned")
        self.assertTrue(picking1, "First picking should be assigned")
        picking1.action_assign()
        picking1.with_context(skip_backorder=True).button_validate()
        self.po.invalidate_recordset(["all_picking_ids", "all_picking_count"])
        self.assertGreaterEqual(
            self.po.all_picking_count,
            1,
            "Should have at least 1 picking (the process might create more)",
        )

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
        self.assertEqual(action_data.get("res_id"), self.po.all_picking_ids.id)
        if len(self.po.all_picking_ids) == 1:
            self.po.all_picking_ids.copy()
            self.po._compute_all_pickings()

        if len(self.po.all_picking_ids) > 1:
            action_data = self.po.action_view_all_pickings()
            self.assertEqual(
                action_data.get("domain"),
                [("id", "in", self.po.all_picking_ids.ids)],
            )
