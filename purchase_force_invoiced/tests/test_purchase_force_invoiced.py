# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# Copyright 2019 Aleph Objects, Inc.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import fields
from odoo.tests import tagged
from odoo.tests.common import TransactionCase

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


@tagged("post_install", "-at_install")
class TestPurchaseForceInvoiced(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        cls.purchase_order_model = cls.env["purchase.order"]
        cls.purchase_order_line_model = cls.env["purchase.order.line"]
        cls.account_invoice_model = cls.env["account.move"]
        cls.account_invoice_line = cls.env["account.move.line"]
        cls.invoice_account = cls.env["account.account"].search(
            [
                ("account_type", "=", "expense"),
                ("company_id", "=", cls.env.company.id),
            ],
            limit=1,
        )

        # Data
        product_ctg = cls._create_product_category()
        cls.service_1 = cls._create_product("test_product1", product_ctg)
        cls.service_2 = cls._create_product("test_product2", product_ctg)
        cls.customer = cls._create_supplier("Test Supplier")

    @classmethod
    def _create_supplier(cls, name):
        """Create a Partner."""
        return cls.env["res.partner"].create(
            {"name": name, "email": "example@yourcompany.com", "phone": 123456}
        )

    @classmethod
    def _create_product_category(cls):
        product_ctg = cls.env["product.category"].create({"name": "test_product_ctg"})
        return product_ctg

    @classmethod
    def _create_product(cls, name, product_ctg):
        product = cls.env["product.product"].create(
            {
                "name": name,
                "categ_id": product_ctg.id,
                "type": "service",
                "purchase_method": "receive",
            }
        )
        return product

    def test_purchase_order(self):
        po = self.purchase_order_model.create({"partner_id": self.customer.id})
        pol1 = self.purchase_order_line_model.create(
            {
                "name": self.service_1.name,
                "product_id": self.service_1.id,
                "product_qty": 1,
                "product_uom": self.service_1.uom_po_id.id,
                "price_unit": 500.0,
                "date_planned": fields.Date.today(),
                "order_id": po.id,
            }
        )
        pol2 = self.purchase_order_line_model.create(
            {
                "name": self.service_2.name,
                "product_id": self.service_2.id,
                "product_qty": 2,
                "product_uom": self.service_2.uom_po_id.id,
                "price_unit": 500.0,
                "date_planned": fields.Date.today(),
                "order_id": po.id,
            }
        )

        # confirm quotation
        po.button_confirm()
        # update quantities delivered
        pol1.qty_received = 1
        pol2.qty_received = 2

        self.assertEqual(
            po.invoice_status, "to invoice", "The invoice status should be To Invoice"
        )

        action = po.action_create_invoice()
        invoice = self.env["account.move"].browse(action["res_id"])
        self.assertEqual(
            po.invoice_status, "invoiced", "The invoice status should be Invoiced"
        )
        # Reduce the invoiced qty
        for line in pol2.invoice_lines:
            line.with_context(check_move_validity=False).unlink()
        self.assertEqual(
            po.invoice_status, "to invoice", "The invoice status should be To Invoice"
        )
        # We set the force invoiced.
        po.button_done()
        po.force_invoiced = True
        self.assertEqual(
            po.invoice_status, "invoiced", "The invoice status should be Invoiced"
        )
        # We remove the force invoiced.
        po.force_invoiced = False
        self.assertEqual(
            po.invoice_status, "to invoice", "The invoice status should be To Invoice"
        )
        action = po.action_create_invoice()
        invoice = self.env["account.move"].browse(action["res_id"])
        invoice_qty = sum(
            invoice.invoice_line_ids.filtered(
                lambda x: x.product_id.id == self.service_2.id
            ).mapped("quantity")
        )
        self.assertEqual(invoice_qty, 2.0)
