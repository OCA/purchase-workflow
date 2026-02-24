# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from freezegun import freeze_time

from odoo import fields
from odoo.fields import Command

from odoo.addons.base.tests.common import BaseCommon


class TestPurchaseOrderUpdate(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.supplier = cls.env["res.partner"].create(
            {
                "name": "Supplier 1",
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product 1",
            }
        )
        cls.env["product.supplierinfo"].create(
            {
                "partner_id": cls.supplier.id,
                "product_id": cls.product.id,
                "delay": 10,
            }
        )

    def test_confirm_po(self):
        self.env.company.purchase_update_date_planned_at_confirm = True
        with freeze_time("2026-02-10"):
            self.po = self.env["purchase.order"].create(
                {
                    "partner_id": self.supplier.id,
                    "order_line": [
                        Command.create(
                            {
                                "product_id": self.product.id,
                            }
                        )
                    ],
                }
            )
        self.assertEqual(
            fields.Datetime.from_string("2026-02-20"), self.po.date_planned
        )

        with freeze_time("2026-02-13"):
            self.po.button_confirm()
        self.assertEqual(
            fields.Datetime.from_string("2026-02-23"), self.po.date_planned
        )

    def test_confirm_po_no_update(self):
        self.env.company.purchase_update_date_planned_at_confirm = False
        with freeze_time("2026-02-10"):
            self.po = self.env["purchase.order"].create(
                {
                    "partner_id": self.supplier.id,
                    "order_line": [
                        Command.create(
                            {
                                "product_id": self.product.id,
                            }
                        )
                    ],
                }
            )
        self.assertEqual(
            fields.Datetime.from_string("2026-02-20"), self.po.date_planned
        )

        with freeze_time("2026-02-13"):
            self.po.button_confirm()
        self.assertEqual(
            fields.Datetime.from_string("2026-02-20"), self.po.date_planned
        )
