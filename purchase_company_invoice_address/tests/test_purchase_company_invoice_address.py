# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("-at_install", "post_install")
class TestPurchaseCompanyInvoiceAddress(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company_partner = cls.company_data["company"].partner_id
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Service",
                "type": "service",
                "purchase_method": "purchase",
                "supplier_taxes_id": False,
            }
        )

    def _create_purchase_order(self):
        return self.env["purchase.order"].create(
            {
                "partner_id": self.partner_a.id,
                "order_line": [
                    Command.create({"product_id": self.product.id, "product_qty": 1.0})
                ],
            }
        )

    def _create_invoice_address(self):
        return self.env["res.partner"].create(
            {
                "name": "Branch",
                "parent_id": self.company_partner.id,
                "type": "invoice",
            }
        )

    def test_default_without_invoice_address(self):
        """Without a dedicated address, the company partner itself is proposed."""
        order = self._create_purchase_order()
        self.assertEqual(order.company_invoice_address_id, self.company_partner)

    def test_default_with_invoice_address(self):
        """An invoice address of the company is proposed once one exists."""
        address = self._create_invoice_address()
        order = self._create_purchase_order()
        self.assertEqual(order.company_invoice_address_id, address)

    def test_no_address_on_customer_invoice(self):
        """The address is meaningless outside vendor documents."""
        invoice = self.env["account.move"].create(
            {"move_type": "out_invoice", "partner_id": self.partner_a.id}
        )
        self.assertFalse(invoice.company_invoice_address_id)

    def test_address_carried_over_to_vendor_bill(self):
        address = self._create_invoice_address()
        order = self._create_purchase_order()
        order.button_confirm()
        order.action_create_invoice()
        bill = order.invoice_ids
        self.assertEqual(bill.company_invoice_address_id, address)
        # The company's own address must never become the bill partner.
        self.assertEqual(bill.partner_id, self.partner_a)
