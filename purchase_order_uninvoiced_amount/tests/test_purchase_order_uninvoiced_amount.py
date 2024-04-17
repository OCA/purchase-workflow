# Copyright 2020 Tecnativa - Manuel Calero
# Copyright 2020 Tecnativa - Pedro M. Baeza
# Copyright 2021 Tecnativa - Víctor Martínez
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields
from odoo.tests.common import Form, TransactionCase

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


class TestPurchaseOrderUninvoiceAmount(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        # Environmet
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
            {"name": "Partner 1", "supplier_rank": 1, "is_company": True}
        )
        # Category
        cls.product_categ = cls.product_category_model.create({"name": "Test category"})
        cls.uom_categ = cls.env["uom.category"].create({"name": "Category 1"})
        cls.uom1 = cls.env["uom.uom"].create(
            {
                "name": "UOM 1",
                "category_id": cls.uom_categ.id,
                "factor": 1,
                "active": True,
                "uom_type": "reference",
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
                "product_uom": self.product_1.uom_po_id.id,
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
                default_purchase_id=purchase,
                default_partner_id=purchase.partner_id,
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
