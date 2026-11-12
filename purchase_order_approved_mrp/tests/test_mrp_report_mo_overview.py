# Copyright 2026 Versada UAB
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests.common import TransactionCase


class TestMrpReportMoOverview(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.env.company.purchase_approve_active = True
        cls.vendor = cls.env["res.partner"].create({"name": "Test Vendor"})
        cls.component = cls.env["product.product"].create(
            {"name": "Test Component", "type": "product"}
        )
        finished_product = cls.env["product.product"].create(
            {"name": "Test Finished Product", "type": "product"}
        )
        cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": finished_product.product_tmpl_id.id,
                "bom_line_ids": [
                    Command.create({"product_id": cls.component.id, "product_qty": 2.0})
                ],
            }
        )
        cls.production = cls.env["mrp.production"].create(
            {"product_id": finished_product.id, "product_qty": 1.0}
        )
        cls.production.action_confirm()

    def test_approved_order_is_component_replenishment(self):
        order = self.env["purchase.order"].create(
            {
                "partner_id": self.vendor.id,
                "order_line": [
                    Command.create(
                        {"product_id": self.component.id, "product_qty": 2.0}
                    )
                ],
            }
        )
        order.button_confirm()
        order.filtered(lambda order: order.state == "approved").ensure_one()
        self.env.flush_all()
        report_values = self.env["report.mrp.report_mo_overview"]._get_report_data(
            self.production.id
        )
        replenishments = report_values["components"][0]["replenishments"]
        self.assertEqual(len(replenishments), 1)
        self.assertEqual(replenishments[0]["summary"]["name"], order.name)
