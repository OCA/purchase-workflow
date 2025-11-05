# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import Command, fields
from odoo.tests.common import TransactionCase


class TestThreeStepReception(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.wh = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.env.company.id)], limit=1
        )
        cls.partner = cls.env["res.partner"].create({"name": "Test Supplier"})
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "is_storable": True,
                "standard_price": 50.0,
            }
        )
        cls.po = cls.env["purchase.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": cls.product.id,
                            "product_qty": 10.0,
                            "price_unit": 50.0,
                            "date_planned": fields.Datetime.now(),
                        }
                    )
                ],
            }
        )

    def _validate_next_step(self):
        self.po.all_picking_ids.filtered(
            lambda x: x.state == "assigned"
        ).button_validate()
        self.po.invalidate_recordset(["all_picking_ids", "all_picking_count"])

    def test_three_steps_generate_three_pickings(self):
        self.wh.reception_steps = "three_steps"
        self.po.button_confirm()
        self.assertEqual(1, self.po.incoming_picking_count)
        self.assertEqual(1, self.po.all_picking_count)
        self._validate_next_step()
        self.assertEqual(2, self.po.all_picking_count)
        self._validate_next_step()
        self.assertEqual(3, self.po.all_picking_count)
        self.assertEqual(
            self.wh.lot_stock_id,
            self.po.all_picking_ids.filtered(
                lambda x: x.state == "assigned"
            ).location_dest_id,
        )

    def test_picking_of_other_document_excluded(self):
        self.po.button_confirm()
        other_picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.wh.out_type_id.id,
                "location_id": self.wh.lot_stock_id.id,
                "location_dest_id": self.env.ref("stock.stock_location_customers").id,
                "move_ids": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1.0,
                            "location_id": self.wh.lot_stock_id.id,
                            "location_dest_id": self.env.ref(
                                "stock.stock_location_customers"
                            ).id,
                            "reference_ids": [Command.set(self.po.reference_ids.ids)],
                        }
                    )
                ],
            }
        )
        self.assertIn(self.po.reference_ids, other_picking.reference_ids)
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
        self._validate_next_step()
        self._validate_next_step()
        action_data = self.po.action_view_all_pickings()
        self.assertEqual(
            action_data["domain"],
            [("id", "in", self.po.all_picking_ids.ids)],
        )
