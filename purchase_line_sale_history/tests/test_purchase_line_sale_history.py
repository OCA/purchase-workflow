# Copyright 2026 Jarsa
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import Command
from odoo.tests import Form, tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestPurchaseLineSaleHistory(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        attribute = cls.env["product.attribute"].create(
            {
                "name": "Size",
                "value_ids": [
                    Command.create({"name": "S"}),
                    Command.create({"name": "L"}),
                ],
            }
        )
        template = cls.env["product.template"].create(
            {
                "name": "Test History Product",
                "attribute_line_ids": [
                    Command.create(
                        {
                            "attribute_id": attribute.id,
                            "value_ids": [Command.set(attribute.value_ids.ids)],
                        }
                    )
                ],
            }
        )
        cls.variant_1, cls.variant_2 = template.product_variant_ids
        cls.order = cls.env["purchase.order"].create(
            {
                "partner_id": cls.partner_a.id,
                "date_order": "2026-07-10 10:00:00",
                "order_line": [
                    Command.create({"product_id": cls.variant_1.id, "product_qty": 1}),
                    Command.create({"product_id": cls.variant_2.id, "product_qty": 1}),
                ],
            }
        )
        cls.line_1, cls.line_2 = cls.order.order_line

    @classmethod
    def _create_invoice(
        cls, product, invoice_date, qty, move_type="out_invoice", post=True
    ):
        move = cls.env["account.move"].create(
            {
                "move_type": move_type,
                "partner_id": cls.partner_a.id,
                "invoice_date": invoice_date,
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": product.id,
                            "quantity": qty,
                            "price_unit": 10.0,
                        }
                    )
                ],
            }
        )
        if post:
            move.action_post()
        return move

    def _history(self):
        self.order.invalidate_recordset(["sales_history_data"])
        return self.order.sales_history_data

    def test_only_one_checkbox_active(self):
        self.line_1.show_sales_history = True
        self.line_2.show_sales_history = True
        self.assertFalse(self.line_1.show_sales_history)
        self.assertTrue(self.line_2.show_sales_history)

    def test_only_one_checkbox_active_form(self):
        with Form(self.order) as order_form:
            with order_form.order_line.edit(0) as line:
                line.show_sales_history = True
            with order_form.order_line.edit(1) as line:
                line.show_sales_history = True
            # The exclusivity must be applied live, before saving.
            with order_form.order_line.edit(0) as line:
                self.assertFalse(line.show_sales_history)
        self.assertFalse(self.line_1.show_sales_history)
        self.assertTrue(self.line_2.show_sales_history)
        self.assertEqual(self.order.sales_history_line_id, self.line_2)

    def test_sales_history_hidden_without_active_line(self):
        self.assertFalse(self.order.sales_history_data)

    def test_sales_history_data_computation(self):
        self._create_invoice(self.variant_1, "2026-02-14", 5)
        self._create_invoice(self.variant_1, "2026-02-20", 2, move_type="out_refund")
        self._create_invoice(self.variant_1, "2025-11-03", 3)
        self.line_1.show_sales_history = True
        history = self._history()
        self.assertEqual(history["product_name"], self.variant_1.display_name)
        self.assertEqual(history["years"], [2026, 2025, 2024])
        self.assertEqual(history["data"]["2026"][1], 3)  # Feb: 5 - 2 refund
        self.assertEqual(history["data"]["2025"][10], 3)  # Nov 2025
        self.assertEqual(history["data"]["2026"][0], 0)  # Jan: no sales
        # Months after the order date (July) have no data yet.
        self.assertIsNone(history["data"]["2026"][11])
        self.assertEqual(history["data"]["2024"], [0] * 12)

    def test_sales_history_excludes_draft_invoices(self):
        self._create_invoice(self.variant_1, "2026-03-10", 7, post=False)
        self.line_1.show_sales_history = True
        history = self._history()
        self.assertEqual(history["data"]["2026"][2], 0)

    def test_sales_history_year_range(self):
        self.order.date_order = "2026-01-15 10:00:00"
        self.line_1.show_sales_history = True
        history = self._history()
        self.assertEqual(history["years"], [2026, 2025, 2024])
        # Every month after January of the current year is still unknown.
        self.assertEqual(history["data"]["2026"][1:], [None] * 11)

    def test_sales_history_years_back_configurable(self):
        default_years = self.env["res.config.settings"].default_get(
            ["purchase_sales_history_years"]
        )["purchase_sales_history_years"]
        self.assertEqual(default_years, 2)
        self.line_1.show_sales_history = True
        self.assertEqual(self._history()["years"], [2026, 2025, 2024])
        self.env["res.config.settings"].create(
            {"purchase_sales_history_years": 4}
        ).execute()
        self.assertEqual(self._history()["years"], [2026, 2025, 2024, 2023, 2022])
        self.env["res.config.settings"].create(
            {"purchase_sales_history_years": 1}
        ).execute()
        self.assertEqual(self._history()["years"], [2026, 2025])

    def test_sales_history_exact_product_id(self):
        self._create_invoice(self.variant_1, "2026-05-05", 5)
        self._create_invoice(self.variant_2, "2026-05-06", 8)
        self.line_1.show_sales_history = True
        self.assertEqual(self._history()["data"]["2026"][4], 5)
        self.line_2.show_sales_history = True
        history = self._history()
        self.assertEqual(history["product_name"], self.variant_2.display_name)
        self.assertEqual(history["data"]["2026"][4], 8)
