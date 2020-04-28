# Copyright 2017 Today Mourad EL HADJ MIMOUNE @ Akretion
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.tests.common import TransactionCase


class TestPurchaseAllowedProduct(TransactionCase):

    def setUp(self):
        super(TestPurchaseAllowedProduct, self).setUp()
        self.supplierinfo_model = self.env['product.supplierinfo']
        self.product_model = self.env['product.product']
        self.partner_4 = self.env.ref('base.res_partner_4')
        self.supplierinfo = self.supplierinfo_model.search(
            [('name', '=', self.partner_4.id)]
        )
        self.prtner_4_supplied_products = self.product_model.search(
            [('product_tmpl_id', 'in',
              [x.product_tmpl_id.id for x in self.supplierinfo])])

    def new_purchase(self):
        """Create an empty purchase."""
        new = self.env["purchase.order"].new()
        return new

    def new_invoice(self):
        """Create an empty purchase."""
        new = self.env["account.invoice"].new()
        return new

    def set_purchase_partner(self, partner):
        self.purchase.partner_id = partner

        # It triggers onchange
        self.purchase.partner_id_change()

        # Ensure the use_only_supplied_product is set
        self.assertEqual(
            self.purchase.use_only_supplied_product,
            partner.use_only_supplied_product)

    def set_invoice_partner(self, partner):
        self.invoice.partner_id = partner

        # It triggers onchange
        self.invoice.partner_id_change()

        # Ensure the use_only_supplied_product is set
        self.assertEqual(
            self.invoice.use_only_supplied_product,
            partner.use_only_supplied_product)

    def test_purchase_onchange(self):
        """A user creates a purchase from the form."""
        self.partner_4.use_only_supplied_product = True

        with self.env.do_in_onchange():
            # User presses ``new``
            self.purchase = self.new_purchase()

            # User changes fields
            self.set_purchase_partner(self.partner_4)

            self.assertEqual(
                self.purchase.use_only_supplied_product, True)
        context = {
            'restrict_supplier_id': self.purchase.partner_id.id,
            'use_only_supplied_product':
            self.purchase.use_only_supplied_product}
        supplied_product = self.product_model.with_context(context)._search([])
        self.assertEqual(
            set(supplied_product), set(self.prtner_4_supplied_products.ids))

    def test_invoice_onchange(self):
        """A user creates a invoice from the form."""
        self.partner_4.use_only_supplied_product = True

        with self.env.do_in_onchange():
            # User presses ``new``
            self.invoice = self.new_invoice()

            # User changes fields
            self.set_invoice_partner(self.partner_4)

            self.assertEqual(
                self.invoice.use_only_supplied_product, True)
        context = {
            'restrict_supplier_id': self.invoice.partner_id.id,
            'use_only_supplied_product':
            self.invoice.use_only_supplied_product}
        supplied_product = self.product_model.with_context(context)._search([])
        self.assertEqual(
            set(supplied_product), set(self.prtner_4_supplied_products.ids))
