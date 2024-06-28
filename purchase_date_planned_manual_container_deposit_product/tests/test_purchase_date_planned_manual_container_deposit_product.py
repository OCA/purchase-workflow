# Copyright 2024 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import datetime, timedelta

from odoo import Command

from odoo.addons.product_packaging_container_deposit.tests.common import Common

time_formate = "%Y-%m-%d %H:%M:%S"


class TestDatePlannedManualContainerDepositProduct(Common):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.order_model = cls.env["purchase.order"]

        cls.next_week_time = datetime.now() + timedelta(days=7)

        cls.order = cls.order_model.create(
            {
                "company_id": cls.env.company.id,
                "partner_id": cls.env.ref("base.res_partner_12").id,
                "state": "draft",
                "date_planned": cls.next_week_time,
                "order_line": [
                    Command.create(
                        {
                            "name": cls.product_a.name,
                            "product_id": cls.product_a.id,
                            "product_qty": 50,
                            "date_planned": cls.next_week_time,
                        }
                    ),
                ],
            }
        )

    def test_do_not_change_date_planned_if_order_confirm(self):
        for order_line in self.order.order_line:
            order_line.write({"price_unit": 120.0})

        self.order.button_confirm()
        self.assertEqual(
            self.order.date_planned.strftime(time_formate),
            self.next_week_time.strftime(time_formate),
            "The date_planned of the PO should not be updated again after order confirm.",
        )

        for order_line in self.order.order_line:
            self.assertEqual(
                order_line.date_planned.strftime(time_formate),
                self.next_week_time.strftime(time_formate),
                "The date_planned of the order line should match the date_planned of PO.",
            )
