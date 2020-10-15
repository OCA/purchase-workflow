# Copyright 2018-2019 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import SUPERUSER_ID, fields
from odoo.tests import common


class TestPurchaseRequestProcurement(common.SavepointCase):
    def setUp(self):
        super(TestPurchaseRequestProcurement, self).setUp()

        # Get required Model
        self.pr_model = self.env["purchase.request"]
        self.prl_model = self.env["purchase.request.line"]
        self.product_uom_model = self.env["uom.uom"]
        self.location = self.env.ref("stock.stock_location_stock")

        # Get required Model data
        self.uom_unit_categ = self.env.ref("uom.product_uom_categ_unit")
        self.product_1 = self.env.ref("product.product_product_16")
        self.product_1.purchase_request = True
        self.product_2 = self.env.ref("product.product_product_13")
        self.uom_unit = self.env.ref("uom.product_uom_unit")

        # Create UoM
        self.uom_ten = self.product_uom_model.create(
            {
                "name": "Ten",
                "category_id": self.uom_unit_categ.id,
                "factor_inv": 10,
                "uom_type": "bigger",
            }
        )

        # Create Supplier
        self.supplier = self.env["res.partner"].create(
            {"name": "Supplier", "is_company": True, "company_id": False}
        )

        # Add supplier to product_1
        self.product_1.write(
            {
                "seller_ids": [
                    (
                        0,
                        0,
                        {"name": self.supplier.id, "price": 100.0, "company_id": False},
                    )
                ]
            }
        )

    def procurement_group_run(self, name, origin, product, qty):
        values = {
            "date_planned": fields.Datetime.now(),
            "warehouse_id": self.env.ref("stock.warehouse0"),
            "route_ids": self.env.ref("purchase_stock.route_warehouse0_buy"),
            "company_id": self.env.ref("base.main_company"),
        }
        procurements = []
        procurements.append(
            self.env["procurement.group"].Procurement(
                product,
                qty,
                product.uom_id,
                self.location,
                name,
                origin,
                self.env.company,
                values,
            )
        )
        return self.env["procurement.group"].run(procurements)

    def test_procure_purchase_request(self):
        has_route = self.procurement_group_run(
            "Test Purchase Request Procurement",
            "Test Purchase Request Procurement",
            self.product_1,
            10,
        )
        self.assertTrue(has_route)
        self.env["procurement.group"].run_scheduler()
        pr = self.env["purchase.request"].search(
            [("origin", "=", "Test Purchase Request Procurement")]
        )
        self.assertTrue(pr.to_approve_allowed)
        self.assertEqual(pr.origin, "Test Purchase Request Procurement")
        prl = self.env["purchase.request.line"].search([("request_id", "=", pr.id)])
        self.assertEqual(prl.request_id, pr)
        # Test split(", ")
        vals = {
            "picking_type_id": self.env.ref("stock.picking_type_in").id,
            "requested_by": SUPERUSER_ID,
            "origin": "Test Origin",
            "line_ids": [
                [
                    0,
                    0,
                    {
                        "product_id": self.env.ref("product.product_product_13").id,
                        "product_uom_id": self.env.ref("uom.product_uom_unit").id,
                        "product_qty": 2.0,
                    },
                ]
            ],
        }
        self.pr_model.create(vals)
        self.procurement_group_run(
            "Test Test, Split", "Test, Split", self.product_1, 10
        )
        self.procurement_group_run("Test Test, Split", False, self.product_1, 10)
