# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from datetime import datetime, timedelta

from freezegun import freeze_time

from odoo.tests.common import SavepointCase

MONDAY = datetime(**{"year": 2022, "month": 6, "day": 13, "hour": 12})
MONDAY_1_WEEK = datetime(**{"year": 2022, "month": 6, "day": 20, "hour": 12})
MONDAY_2_WEEK = datetime(**{"year": 2022, "month": 6, "day": 27, "hour": 12})
MONDAY_3_WEEK = datetime(**{"year": 2022, "month": 7, "day": 4, "hour": 12})
MONDAY_1_WEEK = datetime(**{"year": 2022, "month": 6, "day": 20, "hour": 12})
MONDAY_1_WEEK_AT_11 = datetime(**{"year": 2022, "month": 6, "day": 20, "hour": 11})
MONDAY_2_WEEK_AT_11 = datetime(**{"year": 2022, "month": 6, "day": 27, "hour": 11})
MONDAY_3_WEEK_AT_11 = datetime(**{"year": 2022, "month": 7, "day": 4, "hour": 11})

FUTURE_DAYS = [MONDAY_1_WEEK, MONDAY_2_WEEK, MONDAY_3_WEEK]

DELAYS = [0.0, 0.5, 1.0]

QTY_INCREMENT = 10

# For each monday in the future, before midday, we have -10 qty to order compared
# to midday until the next one.
EXPECTED_QTIES_MAPPING = (
    (MONDAY, 0.0),
    (MONDAY_1_WEEK_AT_11, 0.0),
    (MONDAY_1_WEEK, 10.0),
    (MONDAY_2_WEEK_AT_11, 10.0),
    (MONDAY_2_WEEK, 20.0),
    (MONDAY_3_WEEK_AT_11, 20.0),
    (MONDAY_3_WEEK, 30.0),
)


@freeze_time(MONDAY)
class TestForecastedQty(SavepointCase):
    at_install = False
    post_install = True

    @classmethod
    def setUpClass(cls):
        super(TestForecastedQty, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.setUpClassProduct()
        cls.setUpClassSeller()
        cls.setUpClassOrderpoint()
        cls.setUpClassLocation()
        cls.setUpClassStock()

    @classmethod
    def setUpClassProduct(cls):
        routes = [(6, 0, cls.env.ref("purchase_stock.route_warehouse0_buy").ids)]
        cls.product = cls.env["product.product"].create(
            {
                "name": "Potatoes and Molasses",
                "type": "product",
                "route_ids": routes,
            }
        )

    @classmethod
    def setUpClassSeller(cls):
        cls.suppinfo = cls.env["product.supplierinfo"].create(
            {
                "name": cls.env.ref("base.res_partner_1").id,
                "product_id": cls.product.id,
                "product_tmpl_id": cls.product.product_tmpl_id.id,
            }
        )

    @classmethod
    def setUpClassOrderpoint(cls):
        cls.orderpoint = cls.env["stock.warehouse.orderpoint"].create(
            {"product_id": cls.product.id}
        )

    @classmethod
    def setUpClassLocation(cls):
        cls.location_stock = cls.env.ref("stock.stock_location_stock")
        cls.location_customer = cls.env.ref("stock.stock_location_customers")

    @classmethod
    def setUpClassStock(cls):
        # No stock on first monday, 10 outgoing units ordered every monday after
        for day in FUTURE_DAYS:
            cls.create_move(day, qty=QTY_INCREMENT)

    @classmethod
    def create_move(cls, day, qty=0):
        cls.env["stock.move"].create(
            {
                "name": "Potatoes and Molasses",
                "product_id": cls.product.id,
                "product_uom": cls.product.uom_id.id,
                "location_dest_id": cls.location_customer.id,
                "location_id": cls.location_stock.id,
                "product_uom_qty": qty,
                "date": day,
            }
        )._action_confirm()

    def test_qty_to_order_no_delay(self):
        # In an ideal case, we shouldn't receive the goods before they are leaving
        # the warehouse (especially if goods have an expiration date)
        # To do that, we should be able to order them according to the supplier delay.
        # It means that before we reached `move.date - delay`,
        # we shouldn't need to order goods.
        # This unit test ensures that at `move.date - delay` the qty_to_order is
        # incremented, while at `move.date - delay - 1hour`, it is not.
        for delay in DELAYS:
            self.suppinfo.delay = delay
            for day, expected_qty in EXPECTED_QTIES_MAPPING:
                day -= timedelta(days=delay)
                with freeze_time(day):
                    self.orderpoint._compute_qty()
                    self.assertEqual(expected_qty, self.orderpoint.qty_to_order)
