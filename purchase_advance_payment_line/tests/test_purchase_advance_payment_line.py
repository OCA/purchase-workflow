# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import ValidationError
from odoo.tests import common


class TestPurchaseAdvancePaymentLine(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        # Payment method / mode
        cls.payment_method_out = cls.env.ref(
            "account.account_payment_method_manual_out"
        )
        cls.journal = cls.env["account.journal"].create(
            {
                "name": "Test Payment Journal",
                "code": "TPAY",
                "type": "bank",
            }
        )
        cls.payment_mode = cls.env["account.payment.mode"].create(
            {
                "name": "Test Payment Mode",
                "fixed_journal_id": cls.journal.id,
                "bank_account_link": "variable",
                "payment_method_id": cls.payment_method_out.id,
                "payment_order_ok": True,
            }
        )

        # Partner with the payment mode set as supplier payment mode
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Supplier",
                "supplier_payment_mode_id": cls.payment_mode.id,
            }
        )

        # Products
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "consu",
                "purchase_method": "purchase",
            }
        )

        cls.tax = cls.env["account.tax"].create(
            {
                "name": "Tax 15",
                "type_tax_use": "purchase",
                "amount": 15,
            }
        )

        # Purchase order
        cls.purchase_order = cls.env["purchase.order"].create(
            {"partner_id": cls.partner.id}
        )
        cls.order_line = cls.env["purchase.order.line"].create(
            {
                "order_id": cls.purchase_order.id,
                "product_id": cls.product.id,
                "product_uom": cls.product.uom_id.id,
                "product_qty": 5.0,
                "price_unit": 200.0,
                "taxes_id": cls.tax,
            }
        )
        # Total: 5 * 200 * 1.15 = 1150.0

    def _create_payment_line(self, amount):
        """Helper to create an account.payment.line linked to a purchase order."""
        return (
            self.env["account.payment.line"]
            .with_context(
                bypass_move_line_id_change=True,
                default_payment_mode_id=self.payment_mode.id,
            )
            .create(
                {
                    "purchase_id": self.purchase_order.id,
                    "partner_id": self.partner.id,
                    "currency_id": self.env.company.currency_id.id,
                    "amount_currency": amount,
                    "communication": "Test advance",
                }
            )
        )

    def test_01_create_payment_line_creates_payment_order(self):
        """Creating a payment line without an existing draft order creates one."""
        pline = self._create_payment_line(100.0)
        self.assertTrue(pline.order_id)
        self.assertEqual(pline.order_id.payment_type, "outbound")
        self.assertEqual(pline.order_id.payment_mode_id, self.payment_mode)

    def test_02_create_payment_line_reuses_draft_payment_order(self):
        """A second payment line reuses the existing draft payment order."""
        pline1 = self._create_payment_line(100.0)
        pline2 = self._create_payment_line(200.0)
        self.assertEqual(pline1.order_id, pline2.order_id)

    def test_03_ongoing_payment_line_count_excludes_cancelled(self):
        """ongoing_account_payment_line_count excludes cancelled/uploaded lines."""
        pline = self._create_payment_line(100.0)
        self.assertEqual(self.purchase_order.ongoing_account_payment_line_count, 1)

        # Cancel the parent payment order → line becomes cancelled
        pline.order_id.action_cancel()
        self.purchase_order._compute_account_payment_line_count()
        self.assertEqual(self.purchase_order.ongoing_account_payment_line_count, 0)
        # Total count still includes the cancelled line
        self.assertEqual(self.purchase_order.account_payment_line_count, 1)

    def test_04_action_view_ongoing_payment_lines_list(self):
        """action_view_ongoing_payment_lines returns a list view for multiple lines."""
        for amount in (100.0, 200.0):
            self._create_payment_line(amount)
        action = self.purchase_order.action_view_ongoing_payment_lines()
        self.assertEqual(action["view_mode"], "list")
        self.assertIn(("purchase_id", "=", self.purchase_order.id), action["domain"])

    def test_05_action_view_ongoing_payment_lines_form(self):
        """action_view_ongoing_payment_lines returns a form view for a single line."""
        self._create_payment_line(100.0)
        action = self.purchase_order.action_view_ongoing_payment_lines()
        self.assertEqual(action["view_mode"], "form")

    def test_06_check_amount_positive(self):
        """A non-positive amount raises a ValidationError."""
        with self.assertRaisesRegex(
            ValidationError, "Amount of advance must be positive"
        ):
            self._create_payment_line(0.0)

    def test_07_check_amount_exceeds_residual(self):
        """An amount exceeding the purchase order residual raises a ValidationError."""
        with self.assertRaisesRegex(
            ValidationError,
            "Amount of advance is greater than residual amount on purchase",
        ):
            self._create_payment_line(
                self.purchase_order.amount_residual + 1,
            )

    def test_08_prepare_account_payment_vals_includes_purchase_id(self):
        """_prepare_account_payment_vals includes purchase_id when set."""
        pline = self._create_payment_line(100.0)
        vals = pline._prepare_account_payment_vals()
        self.assertEqual(vals.get("purchase_id"), self.purchase_order.id)
