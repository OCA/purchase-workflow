# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from datetime import timedelta

from odoo import Command, fields
from odoo.tests import TransactionCase, tagged
from odoo.tests.common import Form


@tagged("post_install", "-at_install")
class TestPurchaseDateApprove(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Safety fallback for optional 'order_type' field in Form() tests
        field = cls.env["purchase.order"]._fields.get("order_type")
        comodel_name = getattr(field, "comodel_name", "ir.model")
        cls.order_type_default = cls.env[comodel_name].search([], limit=1).id

        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Partner Test",
                "email": "partner@test.com",
            }
        )

        cls.product = (
            cls.env["product.product"]
            .with_context(mail_create_nosubscribe=True, tracking_disable=True)
            .create(
                {
                    "name": "Product Test",
                    "detailed_type": "consu",
                    "standard_price": 100.0,
                }
            )
        )

    def _create_po(self, vals):
        return (
            self.env["purchase.order"]
            .with_context(default_order_type=self.order_type_default)
            .create(vals)
        )

    def test_edit_date_approve_orm(self):
        purchase_order = self._create_po(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_qty": 1.0,
                            "price_unit": 100.0,
                            "date_planned": fields.Datetime.now(),
                        }
                    )
                ],
            }
        )

        purchase_order.button_confirm()
        self.assertEqual(purchase_order.state, "purchase")
        self.assertTrue(purchase_order.date_approve)

        new_date = fields.Datetime.now() - timedelta(days=2)
        purchase_order.write({"date_approve": new_date})

        self.assertEqual(purchase_order.date_approve, new_date)

    def test_edit_date_approve_view(self):
        purchase_order = self._create_po(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_qty": 5.0,
                            "price_unit": 50.0,
                            "date_planned": fields.Datetime.now(),
                        }
                    )
                ],
            }
        )
        purchase_order.button_confirm()

        test_date = fields.Datetime.now().replace(microsecond=0) - timedelta(hours=5)

        with Form(purchase_order) as po_form:
            po_form.date_approve = test_date
            po_form.save()

        self.assertEqual(purchase_order.partner_id.id, self.partner.id)
        self.assertEqual(purchase_order.date_approve, test_date)

    def test_readonly_when_done(self):
        purchase_order = self._create_po(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_qty": 1.0,
                            "date_planned": fields.Datetime.now(),
                        }
                    )
                ],
            }
        )
        purchase_order.button_confirm()

        purchase_order.button_done()
        self.assertEqual(purchase_order.state, "done")

        with self.assertRaises(AssertionError):
            with Form(purchase_order) as po_form:
                po_form.date_approve = fields.Datetime.now()

    def test_date_approve_required_in_purchase_view(self):
        purchase_order = self._create_po(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_qty": 1.0,
                            "price_unit": 100.0,
                            "date_planned": fields.Datetime.now(),
                        }
                    )
                ],
            }
        )

        purchase_order.button_confirm()
        self.assertEqual(purchase_order.state, "purchase")
        self.assertTrue(purchase_order.date_approve)

        with self.assertRaises(AssertionError):
            with Form(purchase_order) as po_form:
                po_form.date_approve = False
                po_form.save()
