# Copyright 2018-2019 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from freezegun import freeze_time

from odoo import fields
from odoo.tests import common


class TestPurchaseRequestGroupBy(common.SavepointCase):
    def setUp(self):
        super(TestPurchaseRequestGroupBy, self).setUp()

        # Get required Model
        self.pr_model = self.env["purchase.request"]
        self.prl_model = self.env["purchase.request.line"]
        self.product_uom_model = self.env["uom.uom"]
        self.location = self.env.ref("stock.stock_location_stock")
        self.wiz = self.env["purchase.request.line.make.purchase.order"]

        # Get required Model data
        self.uom_unit_categ = self.env.ref("uom.product_uom_categ_unit")
        self.product_1 = self.env.ref("product.product_product_16")
        self.product_1.purchase_request = True
        self.product_2 = self.env.ref("product.product_product_13")
        self.uom_unit = self.env.ref("uom.product_uom_unit")
        # to test company settings
        self.user_admin = self.env.ref("base.user_admin")
        self.env["res.config.settings"].with_user(self.user_admin).create(
            {"company_group_purchase_request": True}
        )

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
                self.env.ref("base.main_company"),
                values,
            )
        )
        return self.env["procurement.group"].run(procurements)

    def test_duplicated_purchase_request(self):
        self.assertEqual(self.env["purchase.request"].search_count([]), 0)
        has_route = self.procurement_group_run(
            "Test Purchase Request Single Line",
            "Test Purchase Request Single Line",
            self.product_1,
            4,
        )
        self.assertTrue(has_route)
        self.env["procurement.group"].run_scheduler()
        pr = self.env["purchase.request"].search(
            [("origin", "=", "Test Purchase Request Single Line")]
        )
        self.assertTrue(pr.to_approve_allowed)
        self.assertEqual(pr.origin, "Test Purchase Request Single Line")

        prl = self.env["purchase.request.line"].search([("request_id", "=", pr.id)])
        self.assertEqual(prl.request_id, pr)
        self.assertEqual(prl.product_qty, 4)
        self.assertEqual(prl.product_id, self.product_1)

        # another request
        has_route = self.procurement_group_run(
            "Test Purchase Request Single Line",
            "Test Purchase Request Single Line",
            self.product_1,
            5,
        )
        self.assertTrue(has_route)
        self.env["procurement.group"].run_scheduler()
        # make sure no new PR is created
        self.assertEqual(self.env["purchase.request"].search_count([]), 1)
        self.assertEqual(len(pr.line_ids), 1)
        self.assertEqual(prl.product_qty, 9)

        # create for another product
        self.assertEqual(self.env["purchase.request"].search_count([]), 1)

        # set purchase_request to True
        self.product_2.purchase_request = True

        has_route = self.procurement_group_run(
            "Test Purchase Request Single Line Prod2",
            "Test Purchase Request Single Line Prod2",
            self.product_2,
            2,
        )
        self.assertTrue(has_route)
        self.env["procurement.group"].run_scheduler()
        pr_2 = self.env["purchase.request"].search(
            [("origin", "=", "Test Purchase Request Single Line Prod2")]
        )
        self.assertTrue(pr_2.to_approve_allowed)
        self.assertEqual(pr_2.origin, "Test Purchase Request Single Line Prod2")

        self.assertEqual(self.env["purchase.request"].search_count([]), 2)
        prl = self.env["purchase.request.line"].search([("request_id", "=", pr_2.id)])
        self.assertEqual(prl.request_id, pr_2)
        self.assertEqual(prl.product_qty, 2)
        self.assertEqual(prl.product_id, self.product_2)

    def test_existing_purchase_request(self):
        with freeze_time("2020-07-03"):
            self.assertEqual(self.env["purchase.request"].search_count([]), 0)
            has_route = self.procurement_group_run(
                "Test Purchase Request Single Line",
                "Test Purchase Request Single Line",
                self.product_1,
                4,
            )
            self.assertTrue(has_route)
            self.env["procurement.group"].run_scheduler()
            pr = self.env["purchase.request"].search(
                [("origin", "=", "Test Purchase Request Single Line")]
            )
            self.assertTrue(pr.to_approve_allowed)
            self.assertEqual(pr.origin, "Test Purchase Request Single Line")

            prl = self.env["purchase.request.line"].search([("request_id", "=", pr.id)])
            self.assertEqual(prl.request_id, pr)
            self.assertEqual(prl.product_qty, 4)
            self.assertEqual(prl.product_id, self.product_1)

        with freeze_time("2020-07-04"):
            # another request
            has_route = self.procurement_group_run(
                "prod_1",
                "prod_1",
                self.product_1,
                5,
            )
            self.assertTrue(has_route)
            self.env["procurement.group"].run_scheduler()
            pr = self.env["purchase.request"].search([("origin", "=", "prod_1")])
            self.product_1.purchase_request = True
            self.assertTrue(pr.to_approve_allowed)
            self.assertEqual(pr.origin, "prod_1")

            prl = self.env["purchase.request.line"].search([("request_id", "=", pr.id)])

            # make sure new PR is created
            self.assertEqual(self.env["purchase.request"].search_count([]), 2)
            self.assertEqual(len(pr.line_ids), 1)
            self.assertEqual(prl.product_qty, 5)


    def test_existing_purchase_request_with_rfq(self):
        self.assertEqual(self.env["purchase.request"].search_count([]), 0)
        has_route = self.procurement_group_run(
            "Test Purchase Request Single Line",
            "Test Purchase Request Single Line",
            self.product_1,
            4,
        )
        self.assertTrue(has_route)
        self.env["procurement.group"].run_scheduler()
        pr = self.env["purchase.request"].search(
            [("origin", "=", "Test Purchase Request Single Line")]
        )
        # self.assertTrue(pr.to_approve_allowed)
        self.assertEqual(pr.origin, "Test Purchase Request Single Line")
        pr.button_to_approve()
        pr.button_approved()
        prl = self.env["purchase.request.line"].search([("request_id", "=", pr.id)])
        self.assertEqual(prl.request_id, pr)
        self.assertEqual(prl.product_qty, 4)
        self.assertEqual(prl.product_id, self.product_1)
        vals = {"supplier_id": self.env.ref("base.res_partner_12").id}
        wiz_id = self.wiz.with_context(
            active_model="purchase.request.line",
            active_ids=[prl.id],
            active_id=prl.id,
        ).create(vals)
        wiz_id.make_purchase_order()
        # make sure rfq is set on the line
        self.assertNotEqual(prl.purchase_state, False)
        self.assertEqual(pr.purchase_count, 1)
        # another request
        has_route = self.procurement_group_run(
            "prod_1",
            "prod_1",
            self.product_1,
            5,
        )
        self.assertTrue(has_route)
        self.env["procurement.group"].run_scheduler()
        pr_2 = self.env["purchase.request"].search([("origin", "=", "prod_1")])
        prl = self.env["purchase.request.line"].search([("request_id", "=", pr_2.id)])
        # make sure new PR is created
        self.assertEqual(self.env["purchase.request"].search_count([]), 2)
        self.assertEqual(len(pr_2.line_ids), 1)
        self.assertEqual(prl.product_qty, 5)
