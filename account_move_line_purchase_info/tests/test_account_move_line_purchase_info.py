# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L. (www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import netsvc
from openerp.tests import common


class TestAccountMoveLinePurchaseInfo(common.TransactionCase):

    def setUp(self):
        super(TestAccountMoveLinePurchaseInfo, self).setUp()
        cr, uid, context = self.cr, self.uid, {}
        self.purchase_model = self.env['purchase.order']
        self.purchase_line_model = self.env['purchase.order.line']
        self.invoice_model = self.env['account.invoice']
        self.invoice_line_model = self.env['account.invoice.line']
        self.product_model = self.env['product.product']
        self.product_ctg_model = self.env['product.category']
        self.acc_type_model = self.env['account.account.type']
        self.account_model = self.env['account.account']
        self.aml_model = self.env['account.move.line']

        self.partner1 = self.env.ref('base.res_partner_1')
        self.location_stock = self.env.ref('stock.stock_location_stock')
        self.purchase_pricelist = self.env.ref('purchase.list0')
        self.company = self.env.ref('base.main_company')

        # Create account for Goods Received Not Invoiced
        acc_type = 'equity'
        name = 'Goods Received Not Invoiced'
        code = 'grni'
        self.account_grni = self._create_account(acc_type, name, code,
                                                 self.company)

        # Create account for Cost of Goods Sold
        acc_type = 'expense'
        name = 'Cost of Goods Sold'
        code = 'cogs'
        self.account_cogs = self._create_account(acc_type, name, code,
                                                 self.company)
        # Create account for Inventory
        acc_type = 'asset'
        name = 'Inventory'
        code = 'inventory'
        self.account_inventory = self._create_account(acc_type, name, code,
                                                      self.company)
        # Create Product
        self.product = self._create_product()

    def _create_account(self, acc_type, name, code, company):
        """Create an account."""
        types = self.acc_type_model.search([('code', '=', acc_type)])
        account = self.account_model.create({
            'name': name,
            'code': code,
            'type': 'other',
            'user_type': types and types[0].id,
            'company_id': company.id
        })
        return account

    def _create_product(self):
        """Create a Product."""
#        group_ids = [group.id for group in groups]
        product_ctg = self.product_ctg_model.create({
            'name': 'test_product_ctg',
            'property_stock_valuation_account_id': self.account_inventory.id
        })
        product = self.product_model.create({
            'name': 'test_product',
            'categ_id': product_ctg.id,
            'type': 'product',
            'standard_price': 1.0,
            'list_price': 1.0,
            'valuation': 'real_time',
            'property_stock_account_input': self.account_grni.id,
            'property_stock_account_output': self.account_cogs.id,
        })
        return product

    def _create_purchase(self, line_products, invoice_method):
        """ Create a purchase order.

        ``line_products`` is a list of tuple [(product, qty)]
        """
        lines = []
        for product, qty in line_products:
            line_values = {
                'product_id': product.id,
                'product_qty': qty,
                'product_uom': product.uom_id.id
            }
            onchange_res = self.purchase_line_model.product_id_change(
                self.purchase_pricelist.id,
                product.id,
                qty,
                product.uom_id.id,
                self.partner1.id)
            line_values.update(onchange_res['value'])
            lines.append(
                (0, 0, line_values)
            )
        return self.purchase_model.create({
            'partner_id': self.partner1.id,
            'location_id': self.location_stock.id,
            'pricelist_id': self.purchase_pricelist.id,
            'order_line': lines,
            'invoice_method': invoice_method
        })

    def _get_balance(self, domain):
        """
        Call read_group method and return the balance of particular account.
        """
        aml_rec = self.aml_model.read_group(domain,
                                            ['debit', 'credit', 'account_id'],
                                            ['account_id'])
        if aml_rec:
            return aml_rec[0].get('debit', 0) - aml_rec[0].get('credit', 0)
        else:
            return 0.0

    def _check_account_balance(self, account_id, purchase_line=None,
                               expected_balance=0.0):
        """
        Check the balance of the account based on different operating units.
        """
        domain = [('account_id', '=', account_id)]
        if purchase_line:
            domain.extend([('purchase_line_id', '=', purchase_line.id)])

        balance = self._get_balance(domain)
        if purchase_line:
            self.assertEqual(
                    balance, expected_balance,
                    'Balance is not %s for Purchase Line %s.'
                    % (str(expected_balance), purchase_line.name))

    def test_purchase_invoice_on_order(self):
        """Test that creating a purchase order with invoicing method on order,
        if we receive the product and we fully invoice the order, the PO
        line has been moved from the invoice and from the stock move to the
        account move line.
        """
        invoice_method = 'order'
        purchase = self._create_purchase([(self.product, 1)], invoice_method)
        po_line = False
        for line in purchase.order_line:
            po_line = line
            break
        purchase.signal_workflow('purchase_confirm')
        picking = purchase.picking_ids
        picking.action_done()
        expected_balance = 1.0
        self._check_account_balance(self.account_inventory.id,
                                    purchase_line=po_line,
                                    expected_balance=expected_balance)

        invoice_id = purchase.action_invoice_create()
        invoice = self.invoice_model.browse(invoice_id)
        invoice.signal_workflow('invoice_open')
        for aml in invoice.move_id.line_id:
            if aml.product_id == po_line.product_id:
                self.assertEqual(aml.purchase_line_id, po_line,
                                 'Purchase Order line has not been copied '
                                 'from the invoice to the account move line.')

    def test_purchase_invoice_po_line(self):
        """Test that creating a purchase order with invoicing based on PO line,
        if we receive the product and we fully invoice the PO line, the PO
        line has been moved from the invoice and from the stock move to the
        account move line.
        """
        invoice_method = 'manual'
        wizard_obj = self.env['purchase.order.line_invoice']
        purchase = self._create_purchase([(self.product, 1)], invoice_method)
        po_line = False
        for line in purchase.order_line:
            po_line = line
            break
        purchase.signal_workflow('purchase_confirm')
        picking = purchase.picking_ids
        picking.action_done()
        expected_balance = 1.0
        self._check_account_balance(self.account_inventory.id,
                                    purchase_line=po_line,
                                    expected_balance=expected_balance)

        wizard = wizard_obj.with_context({
            'active_id': po_line.id,
            'active_ids': [po_line.id],
        }).create({})

        wizard.makeInvoices()
        invoice_lines = self.invoice_line_model.search(
                [('purchase_line_id', '=', po_line.id)])

        for line in invoice_lines:
            for aml in line.invoice_id.move_id.line_id:
                if aml.product_id == po_line.product_id:
                    self.assertEqual(aml.purchase_line_id, po_line,
                                     'Purchase Order line has not been copied '
                                     'from the invoice line to the account '
                                     'move line.')

    def test_purchase_invoice_on_picking(self):
        """Test that creating a purchase order with invoicing based on picking,
        if we receive the product and we fully invoice the PO line, the PO
        line has been moved from the invoice and from the stock move to the
        account move line.
        """
        invoice_method = 'picking'
        wizard_obj = self.env['stock.invoice.onshipping']
        purchase = self._create_purchase([(self.product, 1)], invoice_method)
        po_line = False
        for line in purchase.order_line:
            po_line = line
            break
        purchase.signal_workflow('purchase_confirm')
        picking = purchase.picking_ids
        picking.action_done()
        expected_balance = 1.0
        self._check_account_balance(self.account_inventory.id,
                                    purchase_line=po_line,
                                    expected_balance=expected_balance)

        wizard = wizard_obj.with_context({
            'active_id': picking.id,
            'active_ids': [picking.id],
        }).create({})

        invoice_ids = wizard.create_invoice()
        invoices = self.invoice_model.browse(invoice_ids)

        for invoice in invoices:
            for aml in invoice.move_id.line_id:
                if aml.product_id == po_line.product_id:
                    self.assertEqual(aml.purchase_line_id, po_line,
                                     'Purchase Order line has not been copied '
                                     'from the invoice line to the account '
                                     'move line.')
