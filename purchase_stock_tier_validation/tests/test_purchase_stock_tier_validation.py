# Copyright 2017-2020 ForgeFlow S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo import fields
from odoo.tests import common


class TestPurchaseStockTierValidation(common.TransactionCase):
    def setUp(self):
        super(TestPurchaseStockTierValidation, self).setUp()
        # Get purchase order model
        self.po_model = self.env.ref("purchase.model_purchase_order").with_context(
            tracking_disable=True, no_reset_password=True
        )

        # Create users
        group_ids = self.env.ref("base.group_system").ids
        self.test_user_1 = self.env["res.users"].create(
            {
                "name": "John",
                "login": "test1",
                "groups_id": [(6, 0, group_ids)],
                "email": "test@examlple.com",
            }
        )

        # Create tier definitions:
        self.tier_def_obj = self.env["tier.definition"]
        self.tier_def_obj.create(
            {
                "model_id": self.po_model.id,
                "review_type": "individual",
                "reviewer_id": self.test_user_1.id,
            }
        )

        # Common models
        self.test_partner = self.env["res.partner"].create({"name": "Partner for test"})
        self.stock_loc = self.browse_ref("stock.stock_location_stock")
        self.warehouse = self.browse_ref("stock.warehouse0")

        # Create product
        route_buy = self.env.ref("purchase_stock.route_warehouse0_buy").id
        self.test_product = self.env["product.product"].create(
            {
                "name": "Test Scrap Component 1",
                "type": "product",
                "route_ids": [(6, 0, [route_buy])],
                "seller_ids": [
                    (0, 0, {"partner_id": self.test_partner.id, "price": 20.0})
                ],
            }
        )

    def test_procurement_in_new_rfq(self):
        """
        Procure a product with the same supplier as one open RFQ under validation
        and check if it includes the procurement in that RFQ or in a new one.
        """
        po = self.env["purchase.order"].create(
            {
                "partner_id": self.test_partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": "PO-Product",
                            "product_id": self.test_product.id,
                            "date_planned": fields.Datetime.now(),
                            "product_qty": 10,
                            "product_uom": self.test_product.uom_id.id,
                            "price_unit": 1000,
                        },
                    )
                ],
            }
        )
        rfq_test_partner_before = self.env["purchase.order"].search(
            [("partner_id", "=", self.test_partner.id)]
        )
        self.assertEqual(len(po.mapped("order_line")), 1)
        po.request_validation()
        po.with_user(self.test_user_1).validate_tier()
        date_planned = fields.Datetime.now()
        group = self.env["procurement.group"].create(
            {"name": "Test", "move_type": "direct"}
        )
        values = {
            "company_id": self.warehouse.company_id,
            "group_id": group,
            "date_planned": date_planned,
            "warehouse_id": self.warehouse,
        }
        procurements = [
            self.env["procurement.group"].Procurement(
                self.test_product,
                1,
                self.env.ref("uom.product_uom_unit"),
                self.stock_loc,
                "test",
                "TEST",
                self.warehouse.company_id,
                values,
            )
        ]
        group.run(procurements)
        self.assertEqual(len(po.mapped("order_line")), 1)
        rfq_test_partner_after = self.env["purchase.order"].search(
            [("partner_id", "=", self.test_partner.id)]
        )
        self.assertEqual(len(rfq_test_partner_after), len(rfq_test_partner_before) + 1)
