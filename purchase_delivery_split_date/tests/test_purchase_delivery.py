# Copyright 2014-2016 Numérigraphe SARL
# Copyright 2017 ForgeFlow, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from freezegun import freeze_time

from odoo.fields import Datetime
from odoo.tests.common import Form, TransactionCase


class TestDeliverySingle(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_model = cls.env["product.product"]

        # Create products:
        cls.p1 = cls.product1 = cls.product_model.create(
            {
                "name": "Test Product 1",
                "type": "product",
                "default_code": "PROD1",
                "standard_price": 10,
            }
        )
        cls.p2 = cls.product2 = cls.product_model.create(
            {
                "name": "Test Product 2",
                "type": "product",
                "default_code": "PROD2",
                "standard_price": 10,
            }
        )
        cls.p3 = cls.product2 = cls.product_model.create(
            {
                "name": "Test Product 3",
                "type": "product",
                "default_code": "PROD3",
                "standard_price": 10,
            }
        )

        # Two dates which we can use to test the features:
        cls.date_sooner = "2015-01-01"
        cls.date_later = "2015-12-13"
        cls.date_3rd = "2015-12-31"

        cls.po = cls.env["purchase.order"].create(
            {
                "partner_id": cls.env.ref("base.res_partner_3").id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.p1.id,
                            "product_uom": cls.p1.uom_id.id,
                            "name": cls.p1.name,
                            "price_unit": cls.p1.standard_price,
                            "date_planned": cls.date_sooner,
                            "product_qty": 42.0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": cls.p2.id,
                            "product_uom": cls.p2.uom_id.id,
                            "name": cls.p2.name,
                            "price_unit": cls.p2.standard_price,
                            "date_planned": cls.date_sooner,
                            "product_qty": 12.0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": cls.p1.id,
                            "product_uom": cls.p1.uom_id.id,
                            "name": cls.p1.name,
                            "price_unit": cls.p1.standard_price,
                            "date_planned": cls.date_sooner,
                            "product_qty": 1.0,
                        },
                    ),
                ],
            }
        )

    def test_check_single_date(self):
        """Tests with single date."""
        self.assertEqual(
            len(self.po.picking_ids),
            0,
            "There must not be pickings for the PO when draft",
        )
        self.po.button_confirm()
        self.assertEqual(
            len(self.po.picking_ids),
            1,
            "There must be 1 picking for the PO when confirmed",
        )
        self.assertEqual(
            str(self.po.picking_ids[0].scheduled_date)[:10],
            self.date_sooner,
            "The picking must be planned at the expected date",
        )

    def test_adding_line(self):
        # A modification on line product quantity will recompute the
        # date_planned field with the seller (supplierinfo) lead time
        # Check if the original date planned is kept if new date_planned is before

        # We first add a seller to the product
        self.env["product.supplierinfo"].create(
            {
                "partner_id": self.env.ref("base.res_partner_3").id,
                "product_tmpl_id": self.p1.product_tmpl_id.id,
            }
        )
        # Set today earlier as planned date
        today = "2015-12-01"
        self.po.date_order = today

        self.po.order_line[0].date_planned = self.date_later

        # Then change the line quantity
        with freeze_time(today):
            self.po.order_line[0].product_qty = 43.0

        # We check the later planned date is kept
        self.assertEqual(
            Datetime.to_datetime("2015-12-13"), self.po.order_line[0].date_planned
        )

    def test_check_multiple_dates(self):
        """Tests changing the date of the first line."""
        self.po.order_line[0].date_planned = self.date_later
        self.assertEqual(
            len(self.po.picking_ids),
            0,
            "There must not be pickings for the PO when draft",
        )
        self.po.button_confirm()
        self.assertEqual(
            len(self.po.picking_ids),
            2,
            "There must be 2 pickings for the PO when confirmed. %s found"
            % len(self.po.picking_ids),
        )

        sorted_pickings = sorted(self.po.picking_ids, key=lambda x: x.scheduled_date)
        self.assertEqual(
            str(sorted_pickings[0].scheduled_date)[:10],
            self.date_sooner,
            "The first picking must be planned at the soonest date",
        )
        self.assertEqual(
            str(sorted_pickings[1].scheduled_date)[:10],
            self.date_later,
            "The second picking must be planned at the latest date",
        )

    def test_purchase_line_date_change(self):
        self.po.order_line[0].date_planned = self.date_later
        self.po.button_confirm()
        moves = self.env["stock.move"].search(
            [("purchase_line_id", "=", self.po.order_line[0].id)]
        )
        line = self.po.order_line[0]
        line.write({"date_planned": self.date_3rd})
        self.assertEqual(moves.date_deadline.strftime("%Y-%m-%d"), self.date_3rd)

    def test_group_multiple_picking_same_date(self):
        """Check multiple picking with same planned date are also merged

        This can happen if another module changes the picking planned date
        before the _check_split_pickings is being called from the write method.
        """
        self.po.order_line[0].date_planned = self.date_later
        self.po.button_confirm()
        moves = self.env["stock.move"].search(
            [("purchase_line_id", "in", self.po.order_line.ids)]
        )
        pickings = moves.mapped("picking_id")
        self.assertEqual(len(pickings), 2)
        pickings[1].scheduled_date = pickings[0].scheduled_date
        self.po.order_line[0].date_planned = self.date_sooner
        self.assertEqual(len(moves.mapped("picking_id")), 1)
        self.assertEqual(len(pickings.filtered(lambda r: r.state == "cancel")), 1)

    def test_purchase_line_date_change_split_picking(self):
        self.po.button_confirm()
        line1 = self.po.order_line[0]
        line2 = self.po.order_line[1]
        move1 = self.env["stock.move"].search([("purchase_line_id", "=", line1.id)])
        move2 = self.env["stock.move"].search([("purchase_line_id", "=", line2.id)])

        line1.write({"date_planned": self.date_later})
        self.assertEqual(
            len(self.po.picking_ids),
            2,
            "There must be 2 pickings when I change the date",
        )
        self.assertEqual(move1.date_deadline.strftime("%Y-%m-%d"), self.date_later)
        self.assertEqual(move2.date_deadline.strftime("%Y-%m-%d"), self.date_sooner)
        self.assertNotEqual(move1.picking_id, move2.picking_id)
        line2.write({"date_planned": self.date_later})
        self.assertEqual(
            move1.picking_id,
            move2.picking_id,
            "If I change the other line to the same date as the first, "
            "both moves must be in the same picking",
        )

    def test_purchase_line_created_afer_confirm(self):
        """Check new line created when order is confirmed.

        When a new line is added on an already `purchased` order
        If it is planned for a non yet existing date in the purchase, a
        new picking should be created.

        """
        self.po.button_confirm()
        self.assertEqual(self.po.state, "purchase")
        new_date = "2016-01-30"
        moves_before = self.env["stock.move"].search(
            [("purchase_line_id", "in", self.po.order_line.ids)]
        )
        self.assertEqual(len(moves_before.mapped("picking_id")), 1)
        self.po.order_line = [
            (
                0,
                0,
                {
                    "product_id": self.p3.id,
                    "product_uom": self.p3.uom_id.id,
                    "name": self.p3.name,
                    "price_unit": self.p3.standard_price,
                    "date_planned": new_date,
                    "product_qty": 2.0,
                },
            ),
        ]
        moves_after = self.env["stock.move"].search(
            [("purchase_line_id", "in", self.po.order_line.ids)]
        )
        self.assertEqual(len(moves_after.mapped("picking_id")), 2)

    def test_purchase_line_date_change_tz_aware(self):
        """Check that the grouping  is time zone aware.

        Datetime are always stored in utc in the database.

        """
        self.po.order_line[2].unlink()
        self.po.button_confirm()
        line1 = self.po.order_line[0]
        line2 = self.po.order_line[1]
        self.env.user.tz = "Europe/Brussels"
        self.assertEqual(len(self.po.picking_ids), 1)
        line1.write({"date_planned": "2021-05-05 03:00:00"})
        self.assertEqual(len(self.po.picking_ids), 2)
        # Time difference of at least +1 so  should be same day (1 picking)
        line2.write({"date_planned": "2021-05-04 23:00:00"})
        self.assertEqual(len(self.po.picking_ids), 1)

        self.env.user.tz = "Etc/UTC"
        line1.write({"date_planned": "2021-05-05 03:00:00"})
        self.assertEqual(len(self.po.picking_ids), 2)
        # No time difference so will be another day (2 pickings)
        line2.write({"date_planned": "2021-05-04 23:00:00"})
        self.assertEqual(len(self.po.picking_ids), 2)

    def test_create_from_form(self):
        partner_purchase = self.env["res.partner"].create(
            {"name": "Partner 1 of purchase on create from form"}
        )
        with Form(self.env["purchase.order"]) as purchase_form:
            purchase_form.partner_id = partner_purchase
        self.assertEqual(purchase_form.partner_id, partner_purchase)
