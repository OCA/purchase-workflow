# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.fields import Command

from odoo.addons.base.tests.common import BaseCommon


class TestPurchaseStockTag(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.warehouse.delivery_steps = "pick_ship"
        cls.warehouse.reception_steps = "two_steps"
        cls.warehouse.crossdock_route_id.active = True

        cls.customers = cls.env.ref("stock.stock_location_customers")

        # Rule to Customers has no source location - Put it to Output
        rule = cls.warehouse.crossdock_route_id.rule_ids.filtered(
            lambda rule: rule.location_dest_id == cls.customers
        )
        rule.action = "pull"
        rule.procure_method = "make_to_order"
        rule.location_src_id = cls.warehouse.wh_output_stock_loc_id

        # Rule to Input should trigger another rule (buy)
        rule = cls.warehouse.crossdock_route_id.rule_ids.filtered(
            lambda rule: rule.location_src_id == cls.warehouse.wh_input_stock_loc_id
        )
        rule.procure_method = "make_to_order"
        rule.action = "pull"

        cls.warehouse.buy_pull_id.location_dest_id = cls.warehouse.wh_input_stock_loc_id

        cls.seller = cls.env["res.partner"].create(
            {
                "name": "Test Supplier",
            }
        )

        cls.product = cls.env["product.product"].create(
            {
                "name": "Test",
                "is_storable": True,
                "seller_ids": [
                    Command.create(
                        {
                            "partner_id": cls.seller.id,
                        }
                    )
                ],
            }
        )

        cls.tag = cls.env["purchase.tag"].create({"name": "CROSS"})

        cls.warehouse.crossdock_route_id.purchase_tag_ids = cls.tag
        cls.warehouse.crossdock_route_id.rule_ids.propagate_cancel = True

    @classmethod
    def _create_cross_procurement(cls):
        values = {
            "warehouse_id": cls.warehouse,
            "route_ids": cls.warehouse.crossdock_route_id,
        }
        cls.env["procurement.group"].run(
            [
                cls.env["procurement.group"].Procurement(
                    cls.product,
                    2.0,
                    cls.product.uom_id,
                    cls.customers,
                    "test_mtso_mts_2",
                    "test_mtso_mts_2",
                    cls.warehouse.company_id,
                    values=values,
                )
            ]
        )

    @classmethod
    def _create_customer_procurement(cls):
        values = {
            "warehouse_id": cls.warehouse,
        }
        cls.env["procurement.group"].run(
            [
                cls.env["procurement.group"].Procurement(
                    cls.product,
                    2.0,
                    cls.product.uom_id,
                    cls.customers,
                    "test_mtso_mts_2",
                    "test_mtso_mts_2",
                    cls.warehouse.company_id,
                    values=values,
                )
            ]
        )

    @classmethod
    def _create_purchase_procurement(cls):
        values = {
            "warehouse_id": cls.warehouse,
            "route_ids": cls.warehouse.buy_pull_id.route_id,
        }
        cls.env["procurement.group"].run(
            [
                cls.env["procurement.group"].Procurement(
                    cls.product,
                    2.0,
                    cls.product.uom_id,
                    cls.warehouse.wh_input_stock_loc_id,
                    "test_mtso_mts_2",
                    "test_mtso_mts_2",
                    cls.warehouse.company_id,
                    values=values,
                )
            ]
        )

    def test_purchase_stock_tag(self):
        # Create a procurements using Crossdock route and tagged as 'CROSS'
        # Check the generated purchase order line is tagged with that one
        self._create_cross_procurement()
        line = self.env["purchase.order.line"].search(
            [("product_id", "=", self.product.id)]
        )

        self.assertTrue(line)
        self.assertTrue(line.tag_ids)
        self.assertEqual(line.tag_ids, self.tag)

    def test_purchase_stock_tag_update(self):
        # Create a procurements using Crossdock route and tagged as 'CROSS'
        # Check the generated purchase order line is tagged with that one
        self._create_purchase_procurement()
        self._create_cross_procurement()
        line = self.env["purchase.order.line"].search(
            [("product_id", "=", self.product.id)]
        )

        self.assertTrue(line)
        self.assertTrue(line.tag_ids)
        self.assertEqual(line.tag_ids, self.tag)

    def test_purchase_stock_tag_on_product(self):
        # Create a procurements using Crossdock route and tagged as 'CROSS'
        # Check the generated purchase order line is tagged with that one
        self.product.route_ids |= self.warehouse.crossdock_route_id
        self._create_customer_procurement()
        line = self.env["purchase.order.line"].search(
            [("product_id", "=", self.product.id)]
        )

        self.assertTrue(line)
        self.assertTrue(line.tag_ids)
        self.assertEqual(line.tag_ids, self.tag)
