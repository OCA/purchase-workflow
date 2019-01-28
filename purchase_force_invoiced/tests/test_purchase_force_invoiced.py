# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# Copyright 2019 Aleph Objects, Inc.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields
from odoo.tests.common import TransactionCase


class TestPurchaseForceInvoiced(TransactionCase):

    def setUp(self):
        super(TestPurchaseForceInvoiced, self).setUp()
        self.purchase_order_model = self.env['purchase.order']
        self.purchase_order_line_model = self.env['purchase.order.line']
        self.account_invoice_model = self.env['account.invoice']
        self.account_invoice_line = self.env['account.invoice.line']

        # Data
        product_ctg = self._create_product_category()
        self.service_1 = self._create_product('test_product1',
                                              product_ctg)
        self.service_2 = self._create_product('test_product2',
                                              product_ctg)
        self.customer = self._create_supplier('Test Supplier')

    def _create_supplier(self, name):
        """Create a Partner."""
        return self.env['res.partner'].create({
            'name': name,
            'email': 'example@yourcompany.com',
            'supplier': True,
            'phone': 123456,
        })

    def _create_product_category(self):
        product_ctg = self.env['product.category'].create({
            'name': 'test_product_ctg',
        })
        return product_ctg

    def _create_product(self, name, product_ctg):
        product = self.env['product.product'].create({
            'name': name,
            'categ_id': product_ctg.id,
            'type': 'service',
            'purchase_method': 'receive',
        })
        return product

    def _create_invoice_from_purchase(self, purchase):

        invoice = self.account_invoice_model.create({
            'partner_id': purchase.partner_id.id,
            'purchase_id': purchase.id,
            'account_id': purchase.partner_id.property_account_payable_id.id,
            'type': 'in_invoice',
        })
        invoice.purchase_order_change()

        return invoice

    def test_purchase_order(self):
        po = self.purchase_order_model.create({
            'partner_id': self.customer.id,
        })
        pol1 = self.purchase_order_line_model.create({
            'name': self.service_1.name,
            'product_id': self.service_1.id,
            'product_qty': 1,
            'product_uom': self.service_1.uom_po_id.id,
            'price_unit': 500.0,
            'date_planned': fields.Date.today(),
            'order_id': po.id
        })
        pol2 = self.purchase_order_line_model.create({
            'name': self.service_2.name,
            'product_id': self.service_2.id,
            'product_qty': 2,
            'product_uom': self.service_2.uom_po_id.id,
            'price_unit': 500.0,
            'date_planned': fields.Date.today(),
            'order_id': po.id
        })

        # confirm quotation
        po.button_confirm()
        # update quantities delivered
        pol1.qty_received = 1
        pol2.qty_received = 2

        self.assertEquals(po.invoice_status, 'to invoice',
                          "The invoice status should be To Invoice")

        self._create_invoice_from_purchase(po)
        self.assertEquals(po.invoice_status, 'invoiced',
                          "The invoice status should be Invoiced")

        # Reduce the invoiced qty
        for line in pol2.invoice_lines:
            line.quantity = 1
        self.assertEquals(po.invoice_status, 'to invoice',
                          "The invoice status should be To Invoice")
        # We set the force invoiced.
        po.button_done()
        po.force_invoiced = True
        self.assertEquals(po.invoice_status, 'invoiced',
                          "The invoice status should be Invoiced")
        invoice = self._create_invoice_from_purchase(po)
        invoice_qty = sum(invoice.mapped('invoice_line_ids.quantity'))
        self.assertEqual(invoice_qty, 0.0)
        # We remove the force invoiced.
        po.force_invoiced = False
        self.assertEquals(po.invoice_status, 'to invoice',
                          "The invoice status should be To Invoice")
        invoice = self._create_invoice_from_purchase(po)
        invoice_qty = sum(invoice.mapped('invoice_line_ids.quantity'))
        self.assertEqual(invoice_qty, 1.0)
