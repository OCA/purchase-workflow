# Copyright 2023 Ecosoft Co., Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.addons.purchase_deposit.tests.test_purchase_deposit import TestPurchaseDeposit


class TestPurchaseDepositAnalytic(TestPurchaseDeposit):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.plan_a = cls.env["account.analytic.plan"].create({"name": "Plan A"})
        cls.analytic_account = cls.env["account.analytic.account"].create(
            {"name": "Test Analytic Account", "plan_id": cls.plan_a.id}
        )

    def test_create_deposit_with_analytic(self):
        """Create deposit invoice and ensure analytic_distribution is passed to the
        deposit purchase order line."""
        # Set analytic_distribution on the PO line
        self.po.order_line.analytic_distribution = {str(self.analytic_account.id): 100}
        self.po.button_confirm()

        ctx = {
            "active_id": self.po.id,
            "active_ids": [self.po.id],
            "active_model": "purchase.order",
            "create_bills": True,
        }
        Wizard = self.env["purchase.advance.payment.inv"].with_context(**ctx)
        # default_get should pick up the analytic distribution
        defaults = Wizard.default_get(["analytic_distribution"])
        self.assertEqual(
            defaults.get("analytic_distribution"),
            {str(self.analytic_account.id): 100},
        )

        # Create the deposit
        wizard = Wizard.create({"advance_payment_method": "percentage", "amount": 10})
        wizard.deposit_account_id = self.account_deposit
        wizard.analytic_distribution = {str(self.analytic_account.id): 100}
        wizard.create_invoices()

        # The deposit PO line should have the analytic_distribution
        deposit_line = self.po.order_line.filtered("is_deposit")
        self.assertEqual(
            deposit_line.analytic_distribution,
            {str(self.analytic_account.id): 100},
        )
