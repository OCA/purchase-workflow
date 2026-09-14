# Copyright 2020 Tecnativa - Manuel Calero
# Copyright 2020 Tecnativa - Pedro M. Baeza
# Copyright 2021 Tecnativa - Víctor Martínez
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields
from odoo.tests import Form

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


class TestPurchaseOrderUninvoiceAmount(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if not cls.company_data.get("default_journal_purchase"):
            cls.company_data["default_account_payable"] = cls.env[
                "account.account"
            ].create(
                {
                    "name": "Payable",
                    "code": "PAY",
                    "account_type": "liability_payable",
                }
            )
            cls.company_data["default_account_expense"] = cls.env[
                "account.account"
            ].create(
                {
                    "name": "Expense",
                    "code": "EXP",
                    "account_type": "expense",
                }
            )
            cls.company_data["default_account_receivable"] = cls.env[
                "account.account"
            ].create(
                {
                    "name": "Receivable",
                    "code": "REC",
                    "account_type": "asset_receivable",
                }
            )
            cls.company_data["default_journal_purchase"] = cls.env[
                "account.journal"
            ].create(
                {
                    "name": "Purchase Journal",
                    "type": "purchase",
                    "code": "PJ",
                    "default_account_id": cls.company_data[
                        "default_account_expense"
                    ].id,
                }
            )
        cls.purchase_order_model = cls.env["purchase.order"]
        cls.purchase_order_line_model = cls.env["purchase.order.line"]
        cls.account_move_model = cls.env["account.move"]
        cls.res_partner_model = cls.env["res.partner"]
        cls.product_product_model = cls.env["product.product"]
        cls.product_category_model = cls.env["product.category"]
        # Company
        cls.company = cls.env.ref("base.main_company")
        # Partner
        cls.partner = cls.res_partner_model.create(
            {
                "name": "Partner 1",
                "supplier_rank": 1,
                "is_company": True,
                "property_account_receivable_id": cls.company_data[
                    "default_account_receivable"
                ].id,
                "property_account_payable_id": cls.company_data[
                    "default_account_payable"
                ].id,
            }
        )
        # Category
        cls.product_categ = cls.product_category_model.create({"name": "Test category"})
        cls.uom1 = cls.env["uom.uom"].create(
            {
                "name": "UOM 1",
                "relative_factor": 1,
                "active": True,
            }
        )
        # Products
        cls.product_category = cls.env["product.category"].create(
            {"name": "Test Product category"}
        )
        cls.product_1 = cls.env["product.product"].create(
            {
                "name": "Test Sale Product",
                "sale_ok": True,
                "type": "consu",
                "categ_id": cls.product_category.id,
                "description_sale": "Test Description Sale",
                "purchase_method": "receive",
            }
        )

    def _create_purchase(self, product_qty=1, product_received=1):
        """Create a purchase order."""
        purchase = self.purchase_order_model.create(
            {"company_id": self.company.id, "partner_id": self.partner.id}
        )
        purchase_line_1 = self.purchase_order_line_model.create(
            {
                "name": self.product_1.name,
                "product_id": self.product_1.id,
                "product_qty": product_qty,
                "product_uom_id": self.product_1.uom_id.id,
                "price_unit": 100.0,
                "date_planned": fields.Date.today(),
                "order_id": purchase.id,
            }
        )
        purchase.button_confirm()
        # update quantities delivered
        purchase_line_1.qty_received = product_received
        return purchase

    def _create_invoice_from_purchase(self, purchase):
        invoice_form = Form(
            self.account_move_model.with_context(
                default_move_type="in_invoice",
                default_journal_id=self.company_data["default_journal_purchase"].id,
                default_purchase_id=purchase.id,
                default_partner_id=purchase.partner_id.id,
            )
        )
        return invoice_form.save()

    def test_create_purchase_and_not_invoiced(self):
        purchase = self._create_purchase(1, 1)
        self.assertEqual(
            purchase.invoice_status,
            "to invoice",
            "The purchase status should be To Invoice",
        )
        self.assertEqual(
            purchase.amount_uninvoiced,
            purchase.amount_untaxed,
            "The purchase amount uninvoiced must be the amount untaxed",
        )

    def test_create_purchase_and_no_receive(self):
        purchase = self._create_purchase(2, 0)
        self.assertEqual(
            purchase.amount_uninvoiced, 0, "The purchase amount uninvoiced must be 0"
        )

    def test_create_purchase_and_invoiced_a_part(self):
        purchase = self._create_purchase(10, 5)
        self.assertEqual(purchase.amount_uninvoiced, 500)
        invoice = self._create_invoice_from_purchase(purchase)
        with Form(invoice) as invoice_form:
            with invoice_form.invoice_line_ids.edit(0) as line_form:
                line_form.quantity = 3
        self.assertEqual(purchase.amount_uninvoiced, 200)

    def test_create_purchase_create_and_invoiced_with_all_units(self):
        purchase = self._create_purchase(2, 2)
        self._create_invoice_from_purchase(purchase)
        self.assertEqual(
            purchase.amount_uninvoiced, 0, "The purchase amount uninvoiced must be 0"
        )

    def test_create_purchase_qty_0(self):
        purchase = self._create_purchase(0, 0)
        self.assertEqual(purchase.amount_uninvoiced, 0)

    def test_on_ordered_quantities_policy(self):
        self.product_1.purchase_method = "purchase"
        purchase = self._create_purchase(10, 0)
        self.assertEqual(purchase.amount_uninvoiced, 1000)
        invoice = self._create_invoice_from_purchase(purchase)
        with Form(invoice) as invoice_form:
            with invoice_form.invoice_line_ids.edit(0) as line_form:
                line_form.quantity = 6
        self.assertEqual(purchase.amount_uninvoiced, 400)
        self._create_invoice_from_purchase(purchase)
        self.assertEqual(purchase.amount_uninvoiced, 0)

    def test_create_purchase_receive_and_invoice_more_qty(self):
        purchase = self._create_purchase(10, 10)
        self.assertEqual(purchase.amount_uninvoiced, 1000)
        invoice = self._create_invoice_from_purchase(purchase)
        with Form(invoice) as invoice_form:
            with invoice_form.invoice_line_ids.edit(0) as line_form:
                line_form.quantity = 20
        self.assertEqual(purchase.amount_uninvoiced, -1000)
