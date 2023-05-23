# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from datetime import date

from odoo.tests.common import TransactionCase


class TestPurchaseAnalyticGlobal(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.purchase_order_model = cls.env["purchase.order"]
        cls.partner_model = cls.env["res.partner"]
        cls.analytic_account_model = cls.env["account.analytic.account"]
        cls.partner1 = cls.partner_model.create({"name": "Partner1"})
        cls.partner2 = cls.partner_model.create({"name": "Partner2"})
        cls.analytic_account1 = cls.analytic_account_model.create(
            {
                "name": "Analytic Account 1",
                "plan_id": cls.env.ref("analytic.analytic_plan_departments").id,
            }
        )
        cls.analytic_account2 = cls.analytic_account_model.create(
            {
                "name": "Analytic Account 2",
                "plan_id": cls.env.ref("analytic.analytic_plan_projects").id,
            }
        )
        cls.analytic_account1_json = {str(cls.analytic_account1): 100}
        cls.analytic_account2_json = {str(cls.analytic_account2): 100}
        cls.product = cls.env.ref("product.product_product_4")
        cls.purchase_order1 = cls.purchase_order_model.create(
            {
                "partner_id": cls.partner1.id,
                "analytic_distribution": cls.analytic_account1_json,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product.id,
                            "name": cls.product.name,
                            "product_qty": 10,
                            "price_unit": 50,
                            "product_uom": cls.product.uom_id.id,
                            "date_planned": date.today(),
                        },
                    )
                ],
            }
        )
        cls.purchase_order2 = cls.purchase_order_model.create(
            {
                "partner_id": cls.partner2.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product.id,
                            "name": cls.product.name,
                            "product_qty": 5,
                            "price_unit": 40,
                            "analytic_distribution": cls.analytic_account2_json,
                            "product_uom": cls.product.uom_id.id,
                            "date_planned": date.today(),
                        },
                    )
                ],
            }
        )

    def test_purchase_order_check(self):
        self.assertEqual(
            self.purchase_order1.order_line[0].analytic_distribution,
            self.analytic_account1_json,
        )
        self.assertEqual(
            self.purchase_order2.analytic_distribution, self.analytic_account2_json
        )
        self.purchase_order2.order_line = [
            (
                0,
                0,
                {
                    "product_id": self.product.id,
                    "name": self.product.name,
                    "product_qty": 10,
                    "price_unit": 20,
                    "analytic_distribution": self.analytic_account1_json,
                    "product_uom": self.product.uom_id.id,
                    "date_planned": date.today(),
                },
            )
        ]
        self.assertFalse(self.purchase_order2.analytic_distribution)
