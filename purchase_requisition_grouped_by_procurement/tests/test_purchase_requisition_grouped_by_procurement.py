# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests import common


class TestPurchaseRequisitionGgroupedbyProcurement(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.mto = cls.env.ref("stock.route_warehouse0_mto")
        cls.buy = cls.env.ref("purchase_stock.route_warehouse0_buy")
        cls.product_a = cls._create_product(cls, "Test product A")
        cls.product_b = cls._create_product(cls, "Test product B")
        cls.origin = "TEST"
        cls.group = cls.env["procurement.group"].create({"name": "Test"})
        cls.location = cls.env.ref("stock.stock_location_stock")
        cls.stock_location_route = cls.env.ref("purchase_stock.route_warehouse0_buy")
        cls.stock_rule = cls.stock_location_route.rule_ids[0]
        cls.values = {"date_planned": fields.Datetime.now(), "group_id": cls.group}

    def _create_product(self, name):
        return self.env["product.product"].create(
            {
                "name": name,
                "type": "product",
                "purchase_requisition": "tenders",
                "route_ids": [(6, 0, [self.buy.id, self.mto.id])],
            }
        )

    def _set_procurement_by_product(self, group, product):
        procurement = group.Procurement(
            product,
            1,
            product.uom_id,
            self.location,
            False,
            self.origin,
            self.env.company,
            self.values,
        )
        rule = group._get_rule(
            procurement.product_id, procurement.location_id, procurement.values
        )
        return (procurement, rule)

    def _run_procurements(self):
        self.stock_rule._run_buy(
            [
                self._set_procurement_by_product(self.group, self.product_a),
                self._set_procurement_by_product(self.group, self.product_b),
            ]
        )

    def test_purchase_requisition_grouped(self):
        domain = [("state", "=", "draft")]
        self.env["purchase.requisition"].search(domain).unlink()
        self._run_procurements()
        items = self.env["purchase.requisition"].search(domain)
        self.assertEqual(len(items), 1)
        self.assertEqual(items.origin, self.origin)
        self.assertTrue(self.product_a in items.line_ids.mapped("product_id"))
        self.assertTrue(self.product_b in items.line_ids.mapped("product_id"))
