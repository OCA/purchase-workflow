# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from datetime import date

from odoo.tests.common import Form, TransactionCase


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
            {"name": "Analytic Account 1"}
        )
        cls.analytic_account2 = cls.analytic_account_model.create(
            {"name": "Analytic Account 2"}
        )
        cls.product = cls.env.ref("product.product_product_4")
        cls.purchase_order1 = cls.purchase_order_model.create(
            {
                "partner_id": cls.partner1.id,
                "account_analytic_id": cls.analytic_account1.id,
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
                            "account_analytic_id": cls.analytic_account2.id,
                            "product_uom": cls.product.uom_id.id,
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
        purchase_form = Form(self.purchase_order2)
        with purchase_form.order_line.new() as line_form:
            line_form.product_id = self.product
            line_form.name = self.product.name
            line_form.product_qty = 10
            line_form.price_unit = 20
            line_form.account_analytic_id = self.analytic_account1
            line_form.product_uom = self.product.uom_id
            line_form.date_planned = date.today()
        purchase_form.save()
        self.assertFalse(self.purchase_order2.account_analytic_id)
