# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.fields import Command

from odoo.addons.base.tests.common import BaseCommon


class TestPurchaseOrderEtdEta(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.vendor = cls.env["res.partner"].create({"name": "Test Vendor"})
        cls.product = cls.env["product.product"].create({"name": "Test Product"})

    def _create_po(self):
        return self.env["purchase.order"].create(
            {
                "partner_id": self.vendor.id,
                "date_planned": fields.Datetime.now(),
                "order_line": [
                    Command.create(
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_qty": 1.0,
                            "price_unit": 100.0,
                        }
                    )
                ],
            }
        )

    def test_display_expected_arrival(self):
        po = self._create_po()
        self.assertTrue(po.display_expected_arrival())
        po.company_id.hide_expected_arrival_when_eta = True
        self.assertTrue(po.display_expected_arrival())
        po.date_eta = fields.Date.today()
        self.assertFalse(po.display_expected_arrival())
        po.date_planned = False
        po.company_id.hide_expected_arrival_when_eta = False
        self.assertFalse(po.display_expected_arrival())
