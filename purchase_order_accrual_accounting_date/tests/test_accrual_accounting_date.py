# Copyright 2026 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html).
from odoo import Command, fields
from odoo.exceptions import UserError
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestAccrualAccountingDate(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {
                "name": "Sirloin",
                "type": "consu",
                "purchase_method": "receive",
                "standard_price": 30.0,
            }
        )
        cls.account_expense = cls.company_data["default_account_expense"]
        cls.product.property_account_expense_id = cls.account_expense
        cls.account_accrued = cls.env["account.account"].create(
            {
                "name": "Accrued expenses",
                "code": "ACCRUED",
                "account_type": "liability_current",
            }
        )
        cls.purchase_order = cls.env["purchase.order"].create(
            {
                "partner_id": cls.partner_a.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": cls.product.id,
                            "product_qty": 10.0,
                            "price_unit": 30.0,
                            "taxes_id": False,
                        }
                    )
                ],
            }
        )
        cls.purchase_order.button_confirm()

    def _set_setting(self, enabled):
        self.env.company.accrual_use_accounting_date = enabled

    def _receive(self, date):
        """Receive the whole order with the given effective date."""
        picking = self.purchase_order.picking_ids
        picking.move_ids.write({"quantity": 10.0, "picked": True})
        picking.button_validate()
        picking.move_ids.write({"date": fields.Date.to_date(date)})

    def _bill(self, invoice_date, date=None):
        """Create and post a vendor bill for the whole order.

        Args:
            invoice_date (str): Bill date.
            date (str): Accounting date. Defaults to the one Odoo computes.

        Returns:
            account.move: The vendor bill.
        """
        po_line = self.purchase_order.order_line
        bill = self.env["account.move"].create(
            {
                "move_type": "in_invoice",
                "partner_id": self.partner_a.id,
                "invoice_date": invoice_date,
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "quantity": 10.0,
                            "price_unit": 30.0,
                            "tax_ids": False,
                            "purchase_line_id": po_line.id,
                        }
                    )
                ],
            }
        )
        if date:
            bill.date = date
        bill.action_post()
        return bill

    def _accrue(self, date):
        """Run the accrual wizard and return the expense balance accrued.

        Args:
            date (str): Accrual date.

        Returns:
            float: Balance of the expense line in the accrual entry.
        """
        # Start with a clean cache, as a new request from the user would do
        self.env.invalidate_all()
        wizard = (
            self.env["account.accrued.orders.wizard"]
            .with_context(
                active_model="purchase.order",
                active_ids=self.purchase_order.ids,
            )
            .create({"account_id": self.account_accrued.id, "date": date})
        )
        moves = self.env["account.move"].search(wizard.create_entries()["domain"])
        accrual = moves.filtered(lambda m: m.date == fields.Date.to_date(date))
        return sum(
            accrual.line_ids.filtered(
                lambda line: line.account_id == self.account_expense
            ).mapped("balance")
        )

    def test_bill_booked_and_received_after_accrual_date(self):
        """Bill dated before the accrual date, booked and received after it.

        Odoo credits the expense account, so its reversal doubles the
        expense in the next period. By accounting date, nothing is booked
        nor received yet, so there is nothing to accrue.
        """
        self._bill("2020-08-28", "2020-09-01")
        self._receive("2020-09-01")
        self._set_setting(False)
        self.assertEqual(self._accrue("2020-08-31"), -300.0)
        self._set_setting(True)
        with self.assertRaises(UserError):
            self._accrue("2020-08-31")

    def test_received_before_accrual_date_bill_booked_after(self):
        """Goods received before the accrual date, bill booked after it.

        Odoo sees it as billed and accrues nothing. By accounting date, the
        expense is not in the ledger yet, so the received goods are accrued.
        """
        self._receive("2020-08-20")
        self._bill("2020-08-28", "2020-09-01")
        self._set_setting(False)
        with self.assertRaises(UserError):
            self._accrue("2020-08-31")
        self._set_setting(True)
        self.assertEqual(self._accrue("2020-08-31"), 300.0)

    def test_bill_booked_before_receipt(self):
        """Bill booked before the accrual date, goods received after it.

        The expense is really in the ledger before the goods arrive, so both
        criteria credit the expense account.
        """
        self._bill("2020-08-28")
        self._receive("2020-09-01")
        for enabled in (False, True):
            self._set_setting(enabled)
            self.assertEqual(self._accrue("2020-08-31"), -300.0)

    def test_same_bill_and_accounting_date(self):
        """When both dates match, both criteria give the same result."""
        self._receive("2020-08-10")
        self._bill("2020-08-20")
        for enabled in (False, True):
            self._set_setting(enabled)
            self.assertEqual(self._accrue("2020-08-15"), 300.0)
            with self.assertRaises(UserError):
                self._accrue("2020-08-31")
