# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 (https://www.gnu.org/licenses/agpl-3.0.html)

from odoo import Command
from odoo.exceptions import UserError
from odoo.tests import tagged

from odoo.addons.base.tests.common import BaseCommon


@tagged("post_install", "-at_install")
class TestPurchaseOrderLineCopy(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_a = cls.env["product.product"].create({"name": "Product A"})
        cls.product_b = cls.env["product.product"].create({"name": "Product B"})
        cls.po = cls.env["purchase.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": cls.product_a.id,
                            "product_qty": 10.0,
                            "price_unit": 5.0,
                        }
                    ),
                    Command.create(
                        {
                            "product_id": cls.product_b.id,
                            "product_qty": 3.0,
                            "price_unit": 7.0,
                        }
                    ),
                ],
            }
        )
        cls.line_a = cls.po.order_line.filtered(
            lambda line: line.product_id == cls.product_a
        )

    def test_copy_pol(self):
        lines = self.po.order_line
        self.line_a.copy_pol()
        new_line = self.po.order_line - lines
        self.assertEqual(len(new_line), 1)
        self.assertEqual(new_line.product_id, self.product_a)
        self.assertEqual(new_line.product_qty, 10.0)
        self.assertEqual(new_line.price_unit, 5.0)

    def test_copy_pol_multiple_lines(self):
        self.po.order_line.copy_pol()
        self.assertEqual(len(self.po.order_line), 4)

    def test_copy_pol_cancelled(self):
        self.po.button_cancel()
        with self.assertRaisesRegex(UserError, "canceled or locked"):
            self.line_a.copy_pol()

    def test_copy_pol_locked(self):
        self.po.button_confirm()
        self.po.button_lock()
        with self.assertRaisesRegex(UserError, "canceled or locked"):
            self.line_a.copy_pol()
