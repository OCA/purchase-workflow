# Copyright 2017 Today Mourad EL HADJ MIMOUNE @ Akretion
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.tests.common import Form, TransactionCase


class TestPurchaseAllowedProduct(TransactionCase):
    def setUp(self):
        super().setUp()
        self.supplierinfo_model = self.env["product.supplierinfo"]
        self.product_model = self.env["product.product"]
        self.partner_4 = self.env.ref("base.res_partner_4")
        self.supplierinfo = self.supplierinfo_model.search(
            [("name", "=", self.partner_4.id)]
        )
        self.partner_4_supplied_products = self.product_model.search(
            [
                (
                    "product_tmpl_id",
                    "in",
                    [x.product_tmpl_id.id for x in self.supplierinfo],
                )
            ]
        )

    def test_purchase_onchange(self):
        """A user creates a purchase from the form."""
        self.partner_4.use_only_supplied_product = True
        with Form(
            self.env["purchase.order"], view="purchase.purchase_order_form"
        ) as purchase_form:
            purchase_form.partner_id = self.partner_4

            # Ensure the use_only_supplied_product is set
            self.assertEqual(
                purchase_form.use_only_supplied_product,
                self.partner_4.use_only_supplied_product,
            )

            self.assertEqual(purchase_form.use_only_supplied_product, True)
            context = {
                "restrict_supplier_id": purchase_form.partner_id.id,
                "use_only_supplied_product": purchase_form.use_only_supplied_product,
            }
        supplied_product = self.product_model.with_context(context)._search([])
        self.assertEqual(
            set(supplied_product), set(self.partner_4_supplied_products.ids)
        )

    def test_invoice_onchange(self):
        """A user creates a invoice from the form."""
        self.partner_4.use_only_supplied_product = True
        with Form(
            self.env["account.move"].with_context(default_move_type="out_invoice"),
            view="account.view_move_form",
        ) as invoice_form:
            invoice_form.partner_id = self.partner_4

            # Ensure the use_only_supplied_product is set
            self.assertEqual(
                invoice_form.use_only_supplied_product,
                self.partner_4.use_only_supplied_product,
            )

            self.assertEqual(invoice_form.use_only_supplied_product, True)
            context = {
                "restrict_supplier_id": invoice_form.partner_id.id,
                "use_only_supplied_product": invoice_form.use_only_supplied_product,
            }
        supplied_product = self.product_model.with_context(context)._search([])
        self.assertEqual(
            set(supplied_product), set(self.partner_4_supplied_products.ids)
        )
