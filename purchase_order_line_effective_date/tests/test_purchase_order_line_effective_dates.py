# Copyright (C) 2026  Renato Lima - Akretion
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from freezegun import freeze_time

from odoo import fields
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPurchaseOrderLineEffectiveDates(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.picking_type_in = cls.env.ref("stock.picking_type_in")
        cls.picking_type_in.create_backorder = "always"
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product Test",
                "type": "consu",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "purchase_method": "purchase",
            }
        )
        cls.purchase = cls.env["purchase.order"].create(
            {
                "partner_id": cls.partner.id,
                "picking_type_id": cls.picking_type_in.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product.id,
                            "product_qty": 10.0,
                            "product_uom": cls.product.uom_id.id,
                        },
                    )
                ],
            }
        )

    def test_purchase_order_line_effective_date(self):
        """Check effective dates are computed correctly."""
        self.purchase.button_confirm()
        # No Receipt
        self.assertFalse(self.purchase.order_line.effective_date)
        self.assertFalse(self.purchase.order_line.last_effective_date)

        # First Receipt
        first_delivery_dtt = "2026-04-01 10:00:00"
        with freeze_time(first_delivery_dtt):
            first_picking = self.purchase.picking_ids[0]
            first_picking.move_ids.write({"quantity": 3.0})
            first_picking.button_validate()
            self.assertEqual(first_picking.state, "done")

            self.assertRecordValues(
                self.purchase.order_line,
                [
                    {
                        "effective_date": fields.Datetime.from_string(
                            first_delivery_dtt
                        ),
                        "last_effective_date": fields.Datetime.from_string(
                            first_delivery_dtt
                        ),
                    }
                ],
            )

        # Second delivery - Advance time
        second_delivery_dtt = "2026-05-01 12:00:00"
        with freeze_time(second_delivery_dtt):
            self.purchase.invalidate_recordset(["picking_ids"])
            self.assertEqual(len(self.purchase.picking_ids), 2)
            second_picking = self.purchase.picking_ids.filtered(
                lambda p: p.state != "done"
            )
            second_picking.move_ids.write({"quantity": 7.0})
            second_picking.button_validate()
            self.assertEqual(second_picking.state, "done")

            self.assertRecordValues(
                self.purchase.order_line,
                [
                    {
                        "effective_date": fields.Datetime.from_string(
                            first_delivery_dtt
                        ),
                        "last_effective_date": fields.Datetime.from_string(
                            second_delivery_dtt
                        ),
                    }
                ],
            )
