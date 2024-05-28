# Copyright 2024 Akretion (https://www.akretion.com).
# @author Mathieu Delva <mathieu.delva@akretion.com>

import datetime

from odoo import fields
from odoo.tests import common


class TestPurchaseStockSyncScheduleDate(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.po = self.env.ref("purchase_stock.purchase_order_8")

    def test_picking_scheduled_date(self):
        self.po.write(
            {
                "date_planned": fields.Datetime.to_string(
                    datetime.datetime.now() + datetime.timedelta(days=15)
                )
            }
        )
        self.po.onchange_date_planned()
        self.assertEqual(self.po.date_planned, self.po.order_line[0].date_planned)
        self.assertEqual(self.po.date_planned, self.po.picking_ids[0].scheduled_date)
