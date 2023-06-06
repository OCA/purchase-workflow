# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from datetime import date

from odoo.tests.common import TransactionCase


class TestPurchaseAnalyticGlobal(TransactionCase):
    def setUp(self):
        super(TestPurchaseAnalyticGlobal, self).setUp()
        self.purchase_order_model = self.env["purchase.order"]
        self.partner_model = self.env["res.partner"]
        self.analytic_account_model = self.env["account.analytic.account"]
        self.partner1 = self.partner_model.create({"name": "Partner1"})
        self.partner2 = self.partner_model.create({"name": "Partner2"})
        self.analytic_account1 = self.analytic_account_model.create(
            {"name": "Analytic Account 1"}
        )
        self.analytic_account2 = self.analytic_account_model.create(
            {"name": "Analytic Account 2"}
        )
        self.product = self.env.ref("product.product_product_4")
        self.purchase_order1 = self.purchase_order_model.create(
            {
                "partner_id": self.partner1.id,
                "account_analytic_id": self.analytic_account1.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "name": self.product.name,
                            "product_qty": 10,
                            "price_unit": 50,
                            "product_uom": self.product.uom_id.id,
                            "date_planned": date.today(),
                        },
                    )
                ],
            }
        )
        self.purchase_order2 = self.purchase_order_model.create(
            {
                "partner_id": self.partner2.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "name": self.product.name,
                            "product_qty": 5,
                            "price_unit": 40,
                            "account_analytic_id": self.analytic_account2.id,
                            "product_uom": self.product.uom_id.id,
                            "date_planned": date.today(),
                        },
                    )
                ],
            }
        )

    def test_purchase_order_check(self):
        self.assertEqual(
            self.purchase_order1.order_line[0].account_analytic_id,
            self.analytic_account1,
        )
        self.assertEqual(
            self.purchase_order2.account_analytic_id, self.analytic_account2
        )
