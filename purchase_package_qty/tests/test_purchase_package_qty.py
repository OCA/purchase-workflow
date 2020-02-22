##############################################################################
#
#    Copyright (C) 2019-Today: La Louve (<https://cooplalouve.fr>)
#    Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
#    License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
##############################################################################

from odoo.addons.account.tests.account_test_no_chart import TestAccountNoChartCommon
from odoo import fields
from odoo.tests import Form


class TestPurchasePackageQty(TestAccountNoChartCommon):

    def setUp(self):
        super(TestPurchasePackageQty, self).setUp()
        self.supplierinfo_model = self.env['product.supplierinfo']
        self.purchase_order_line_model = self.env['purchase.order.line']
        self.partner_1 = self.env.ref('base.res_partner_1')
        self.partner_2 = self.env.ref('base.res_partner_2')
        self.product = self.env.ref('product.product_product_4d')
        self.Invoice = self.env['account.invoice'].with_context(mail_notrack=True, mail_create_nolog=True)

        self.supplierinfo = self.supplierinfo_model.create({
            'min_qty': 0.0,
            'name': self.partner_2.id,
            'product_tmpl_id': self.product.product_tmpl_id.id,
            'package_qty': 10,
            'price_policy': 'package',
            'base_price': 100,
            'indicative_package': True,
        })

        self.purchase_order = self.env['purchase.order'].create(
            {'partner_id': self.partner_2.id})
        self.po_line_1 = self.purchase_order_line_model.create(
            {'order_id': self.purchase_order.id,
             'product_id': self.product.id,
             'date_planned': fields.Datetime.now(),
             'name': 'Test',
             'product_qty': 1,
             'product_uom': self.env.ref('uom.product_uom_categ_unit').id,
             'price_unit': 10.0})
        self.po_line_1.onchange_product_id()
        self.po_line_1.write({'product_qty_package': 2.0})
        self.po_line_1.onchange_product_qty_package()

    def test_001_purchase_order_partner_2_product_qty_package_2(self):
        self.assertEquals(
            self.po_line_1.product_qty, 20,
            "Incorrect Quantity for product 6 with partner 2 and Number  of "
            "Packages 2: "
            "Quantity Should be 20.")

    def test_002_purchase_order_line_subtotal(self):
        self.assertEquals(
            self.po_line_1.price_subtotal, 200.0,
            "Incorrect Subtotal for product 6 with Price Policy is "
            "per Package, "
            "Number of packages are 2 and Unit Price is 100: "
            "Subtotal should be 200.00")

    def test_003_stock_move_package_qty(self):
        self.purchase_order.button_confirm()
        for move in self.po_line_1.move_ids:
            self.assertEquals(
                move.package_qty, self.po_line_1.package_qty,
                "Incorrect Package Qty in Stock Move, it should be %s" %
                self.po_line_1.package_qty)
            self.assertEquals(
                move.product_qty_package, self.po_line_1.product_qty_package,
                "Incorrect Number of Packages Qty in Stock Move, it should "
                "be %s" % self.po_line_1.product_qty_package)
            move.write({'quantity_done': move.product_uom_qty})
        self.purchase_order.picking_ids.button_validate()
        for move in self.po_line_1.move_ids:
            self.assertEquals(
                move.qty_done_package, move.product_qty_package,
                "Incorrect Done(package) Qty in Stock Move, it should "
                "be %s" % move.product_qty_package)

    def test_004_check_invoice_line_qty(self):
        self.purchase_order.button_confirm()
        self.purchase_order.picking_ids.button_validate()

        invoice = self.Invoice.create({
            'type': 'in_invoice',
            'partner_id': self.partner_customer_usd.id,
            'account_id': self.account_payable.id,
            'journal_id': self.purchae_journal.id,
            'currency_id': self.env.user.company_id.currency_id.id,
            'purchase_id': self.purchase_order.id
        })
        invoice.purchase_order_change()
        for line in invoice.invoice_line_ids:
            self.assertEquals(
                line.package_qty,
                line.purchase_line_id.package_qty,
                "Incorrect Package Qty in Invoice Line, it should "
                "be %s" % line.purchase_line_id.product_qty_package)
            self.assertEquals(
                line.product_qty_package,
                line.purchase_line_id.product_qty_package,
                "Incorrect Number of Packages Qty in Invoice Line, it should "
                "be %s" % line.purchase_line_id.product_qty_package)
            self.assertEquals(
                line.price_policy,
                line.purchase_line_id.price_policy,
                "Incorrect Price Policy in Invoice Line, it should "
                "be %s" % line.purchase_line_id.price_policy)

    def test_005_check_stock_inventory(self):
        inventory_form = Form(self.env['stock.inventory'])
        inventory_form.filter = 'product'
        inventory_form.name = 'Test Stock Inventory'
        inventory_form.product_id = self.product
        inventory = inventory_form.save()
        inventory.action_start()
        for line in inventory.line_ids:
            self.assertEquals(
                line.package_qty,
                self.supplierinfo.package_qty,
                "Incorrect Package Qty in Stock Inventory Line, it should "
                "be %s" % self.supplierinfo.package_qty)
