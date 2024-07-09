# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import TransactionCase


class TestPurchasePackaging(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.line_obj = cls.env["purchase.order.line"]
        cls.partner = cls.env.ref("base.res_partner_12")
        cls.product = cls.env.ref("product.product_product_9")
        cls.packaging = cls.env["product.packaging"].create(
            {"name": "Test packaging", "product_id": cls.product.id, "qty": 5.0}
        )
        cls.packaging_10 = cls.env["product.packaging"].create(
            {"name": "Test packaging", "product_id": cls.product.id, "qty": 10.0}
        )
        cls.packaging_12 = cls.env["product.packaging"].create(
            {"name": "Test packaging 12", "product_id": cls.product.id, "qty": 12.0}
        )
        cls.env.user.groups_id += cls.env.ref("product.group_stock_packaging")
        cls.warehouse = cls.env.ref("stock.warehouse0")

    def test_purchase_packaging_from_procurement(self):
        # Check of packaging is well passed from procurement to purchase line
        # and does not take default one
        lines_before = self.line_obj.search([])
        self.group = self.env["procurement.group"].create({"name": "Test"})
        self.env["procurement.group"].run(
            [
                self.group.Procurement(
                    self.product,
                    20.0,
                    self.product.uom_id,
                    self.warehouse.lot_stock_id,
                    "Product",
                    "Product",
                    company_id=self.env.company,
                    values={"product_packaging_id": self.packaging},
                )
            ]
        )
        lines_after = self.line_obj.search([]) - lines_before

        self.assertTrue(lines_after.product_packaging_id)
        self.assertEqual(lines_after.product_packaging_id, self.packaging)

    def test_purchase_packaging_from_move(self):
        # Check of packaging is well passed from stock move to procurement,
        # then to purchase line and does not take default one
        lines_before = self.line_obj.search([])

        self.move = self.env["stock.move"].create(
            {
                "name": "Product Test",
                "location_dest_id": self.env.ref("stock.stock_location_customers").id,
                "location_id": self.warehouse.lot_stock_id.id,
                "product_id": self.product.id,
                "product_uom_qty": 20.0,
                "product_packaging_id": self.packaging.id,
                "procure_method": "make_to_order",
            }
        )

        self.move._action_confirm()

        lines_after = self.line_obj.search([]) - lines_before

        self.assertTrue(lines_after.product_packaging_id)
        self.assertEqual(lines_after.product_packaging_id, self.packaging)
