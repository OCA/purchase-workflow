# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPurchaseOrderLine(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.user.company_id

        cls.partner = cls.env["res.partner"].create({"name": "Vendor Test"})

        cls.product = cls.env["product.product"].create(
            {
                "name": "Guitar",
                "default_code": "FURN_6666",
                "purchase_ok": True,
            }
        )

        cls.po = cls.env["purchase.order"].create(
            {
                "partner_id": cls.partner.id,
                "company_id": cls.company.id,
            }
        )

    def test_hide_product_code_true(self):
        self.company.hide_product_code = True
        line = self.env["purchase.order.line"].create(
            {
                "order_id": self.po.id,
                "product_id": self.product.id,
                "product_qty": 1.0,
                "price_unit": 100.0,
            }
        )

        self.assertNotIn("[FURN_6666]", line.name)
        self.assertIn("Guitar", line.name)

    def test_hide_product_code_false(self):
        line = self.env["purchase.order.line"].create(
            {
                "order_id": self.po.id,
                "product_id": self.product.id,
                "product_qty": 1.0,
                "price_unit": 100.0,
            }
        )

        self.assertIn("[FURN_6666]", line.name)
        self.assertIn("Guitar", line.name)
