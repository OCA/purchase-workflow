# © 2022 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import timedelta

from freezegun import freeze_time

from odoo.tests import SavepointCase

TIME = "2022-10-03 12:00:00"


class Test(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner = cls.env.ref("base.res_partner_12")
        cls.product = cls.env.ref("product.product_product_9")

    def _create_order(self, freight=None):
        values = {
            "partner_id": self.partner.id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "name": self.product.name,
                        "product_id": self.product.id,
                        "product_uom_qty": 1,
                        "product_uom": self.product.uom_id.id,
                    },
                )
            ],
        }

        if freight:
            values.update(
                {
                    "freight_change_policy": "duration",
                    "receive_date": "2022-10-07",
                    "dispatch_date": "2022-10-07",
                }
            )

        return self.env["purchase.order"].create(values)

    def test_no_freight(self):
        with freeze_time(TIME):
            order = self._create_order()
            # dispatch_date initialized to date planned
            self.assertEqual(order.receive_date, order.dispatch_date)

    def test_plane_freight(self):
        with freeze_time(TIME):
            order = self._create_order(freight=True)

            self.assertEqual(order.freight_duration, 0)

            plane_freight = ref(self, "plane1")
            order.freight_change_policy = "dispatch"
            order.freight_rule_id = plane_freight.id
            self.assertEqual(order.freight_rule_id, plane_freight)
            self.assertEqual(order.freight_duration, order.freight_rule_id.duration)
            self.check_planned_dispatch_date_with_duration(order)

    def test_reset_freight(self):
        with freeze_time(TIME):
            order = self._create_order(freight=True)
            order.freight_change_policy = "dispatch"
            # Original date
            self.assertEqual(order.receive_date.strftime("%Y-%m-%d"), "2022-10-07")
            order.freight_rule_id = ref(self, "plane1").id
            self.check_planned_dispatch_date_with_duration(order)
            order.freight_rule_id = False
            self.assertEqual(order.receive_date.strftime("%Y-%m-%d"), "2022-10-07")

    def test_update_duration_dispatch(self):
        with freeze_time(TIME):
            order = self._create_order(freight=True)
            self.assertEqual(order.receive_date.strftime("%Y-%m-%d"), "2022-10-07")
            self.assertEqual(order.dispatch_date.strftime("%Y-%m-%d"), "2022-10-07")
            order.freight_change_policy = "dispatch"
            order.freight_duration = 4
            self.assertEqual(order.freight_duration, 4)
            self.assertEqual(order.dispatch_date.strftime("%Y-%m-%d"), "2022-10-03")
            self.check_planned_dispatch_date_with_duration(order)
            order.freight_rule_id = ref(self, "plane1").id
            self.assertEqual(order.freight_duration, 2)
            self.assertEqual(order.dispatch_date.strftime("%Y-%m-%d"), "2022-10-05")
            self.check_planned_dispatch_date_with_duration(order)

    def test_update_duration_received(self):
        with freeze_time(TIME):
            order = self._create_order(freight=True)
            self.assertEqual(order.receive_date.strftime("%Y-%m-%d"), "2022-10-07")
            order.freight_change_policy = "receive"
            order.freight_rule_id = ref(self, "plane1").id

            self.assertEqual(order.freight_duration, 2)
            self.assertEqual(order.dispatch_date.strftime("%Y-%m-%d"), "2022-10-07")
            self.assertEqual(order.receive_date.strftime("%Y-%m-%d"), "2022-10-09")
            self.check_planned_dispatch_date_with_duration(order)
            order.freight_duration = 4
            self.assertEqual(order.dispatch_date.strftime("%Y-%m-%d"), "2022-10-07")
            self.assertEqual(order.receive_date.strftime("%Y-%m-%d"), "2022-10-11")
            self.check_planned_dispatch_date_with_duration(order)

    def test_update_receive_date(self):
        with freeze_time(TIME):
            order = self._create_order(freight=True)
            order.freight_change_policy = "dispatch"
            order.freight_rule_id = ref(self, "plane1").id
            order.receive_date = "2022-10-30"
            self.check_planned_dispatch_date_with_duration(order)
            order.receive_date = "2022-10-07"
            self.check_planned_dispatch_date_with_duration(order)
            # order.dispatch_date = "2022-10-28"
            # self.check_planned_dispatch_date_with_duration(order)

    def check_planned_dispatch_date_with_duration(self, order):
        "We check that freight_duration separates receive_date and dispatch_date"
        self.assertEqual(
            order.dispatch_date,
            order.receive_date - timedelta(days=order.freight_duration),
        )

    def test_picking(self):
        with freeze_time(TIME):
            order = self._create_order(freight=True)
            order.freight_change_policy = "dispatch"
            order.freight_duration = 99
            order.button_confirm()
            picking = order.picking_ids[0]
            self.assertEqual(picking.freight_duration, order.freight_duration)


def ref(self, idstring):
    return self.env.ref("purchase_freight_delay.%s" % idstring)
