# Copyright 2026 PopSolutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestPurchaseRequestSmartbutton(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        # The accounting test user has no purchase rights of its own.
        cls.env.user.groups_id |= cls.env.ref(
            "purchase_request.group_purchase_request_manager"
        ) | cls.env.ref("purchase.group_purchase_manager")
        cls.vendor = cls.env["res.partner"].create({"name": "Vendor"})
        cls.product = cls.env["product.product"].create(
            {"name": "Requested product", "type": "consu", "purchase_ok": True}
        )

    def _request_with_line(self, name="request"):
        request = self.env["purchase.request"].create(
            {"requested_by": self.env.user.id}
        )
        line = self.env["purchase.request.line"].create(
            {
                "request_id": request.id,
                "product_id": self.product.id,
                "name": name,
                "product_qty": 3.0,
            }
        )
        return request, line

    def _order_for(self, request_lines):
        order = self.env["purchase.order"].create(
            {
                "partner_id": self.vendor.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "name": self.product.name,
                            "product_qty": 3.0,
                            "price_unit": 10.0,
                            "date_planned": "2026-01-01",
                            "purchase_request_lines": [(6, 0, request_lines.ids)],
                        },
                    )
                ],
            }
        )
        return order

    def _bill_for(self, orders):
        bill = self.env["account.move"].create(
            {
                "move_type": "in_invoice",
                "partner_id": self.vendor.id,
                "invoice_date": "2026-01-05",
                "date": "2026-01-05",
                "journal_id": self.company_data["default_journal_purchase"].id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "name": self.product.name,
                            "quantity": 3.0,
                            "price_unit": 10.0,
                            "purchase_line_id": line.id,
                        },
                    )
                    for line in orders.order_line
                ],
            }
        )
        return bill

    # -- purchase order --------------------------------------------------
    def test_order_reaches_its_request(self):
        request, line = self._request_with_line()
        order = self._order_for(line)
        self.assertEqual(order.purchase_request_ids, request)
        self.assertEqual(order.purchase_request_count, 1)

    def test_order_without_request_shows_nothing(self):
        order = self.env["purchase.order"].create(
            {
                "partner_id": self.vendor.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "name": self.product.name,
                            "product_qty": 1.0,
                            "price_unit": 10.0,
                            "date_planned": "2026-01-01",
                        },
                    )
                ],
            }
        )
        self.assertFalse(order.purchase_request_ids)
        self.assertEqual(order.purchase_request_count, 0)

    def test_order_serving_two_requests_lists_both(self):
        first, first_line = self._request_with_line("first")
        second, second_line = self._request_with_line("second")
        order = self._order_for(first_line | second_line)
        self.assertEqual(order.purchase_request_ids, first | second)
        self.assertEqual(order.purchase_request_count, 2)

    # -- vendor bill -------------------------------------------------------
    def test_bill_reaches_the_request_of_its_order(self):
        request, line = self._request_with_line()
        order = self._order_for(line)
        bill = self._bill_for(order)
        self.assertEqual(bill.purchase_request_ids, request)

    def test_bill_consolidating_two_orders_reaches_both_requests(self):
        """Regression: only the first order used to be looked at."""
        first, first_line = self._request_with_line("first")
        second, second_line = self._request_with_line("second")
        first_order = self._order_for(first_line)
        second_order = self._order_for(second_line)
        bill = self._bill_for(first_order | second_order)

        self.assertEqual(bill.purchase_request_ids, first | second)
        self.assertEqual(bill.purchase_request_count, 2)

    def test_bill_without_purchase_order_shows_nothing(self):
        bill = self.env["account.move"].create(
            {
                "move_type": "in_invoice",
                "partner_id": self.vendor.id,
                "invoice_date": "2026-01-05",
                "date": "2026-01-05",
                "journal_id": self.company_data["default_journal_purchase"].id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "name": self.product.name,
                            "quantity": 1.0,
                            "price_unit": 10.0,
                        },
                    )
                ],
            }
        )
        self.assertFalse(bill.purchase_request_ids)

    # -- the button --------------------------------------------------------
    def test_button_opens_the_form_of_a_single_request(self):
        request, line = self._request_with_line()
        order = self._order_for(line)
        action = order.action_view_purchase_requests()
        self.assertEqual(action["view_mode"], "form")
        self.assertEqual(action["res_id"], request.id)

    def test_button_opens_the_list_of_several_requests(self):
        first, first_line = self._request_with_line("first")
        second, second_line = self._request_with_line("second")
        order = self._order_for(first_line | second_line)
        action = order.action_view_purchase_requests()
        self.assertEqual(action["view_mode"], "tree,form")
        self.assertEqual(sorted(action["domain"][0][2]), sorted((first | second).ids))

    def test_button_from_the_bill(self):
        request, line = self._request_with_line()
        bill = self._bill_for(self._order_for(line))
        action = bill.action_view_purchase_requests()
        self.assertEqual(action["res_id"], request.id)
