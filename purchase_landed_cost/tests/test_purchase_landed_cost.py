# Copyright 2018 Tecnativa - Vicent Cubells
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.exceptions import UserError
from odoo.tests import common


class TestPurchaseLandedCost(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestPurchaseLandedCost, cls).setUpClass()
        cls.type_amount = cls.env['purchase.expense.type'].create({
            'name': 'Type Amount',
            'calculation_method': 'amount',
            'default_amount': True,
        })
        cls.type_price = cls.env['purchase.expense.type'].create({
            'name': 'Type Price',
            'calculation_method': 'price',
        })
        cls.type_qty = cls.env['purchase.expense.type'].create({
            'name': 'Type Qty',
            'calculation_method': 'qty',
        })
        cls.type_weight = cls.env['purchase.expense.type'].create({
            'name': 'Type Weight',
            'calculation_method': 'weight',
        })
        cls.type_volume = cls.env['purchase.expense.type'].create({
            'name': 'Type Volume',
            'calculation_method': 'volume',
        })
        cls.type_equal = cls.env['purchase.expense.type'].create({
            'name': 'Type Equal',
            'calculation_method': 'equal',
        })
        cls.distribution = cls.env['purchase.cost.distribution'].create({
            'name': '/',
        })
        cls.product = cls.env['product.product'].create({
            'name': 'Product',
            'type': 'product',
            'standard_price': 3.0,
            'property_cost_method': 'average',
        })
        cls.service = cls.env['product.product'].create({
            'name': 'Service',
            'type': 'service',
            'standard_price': 10.0,
        })
        categ_unit = cls.env.ref('product.product_uom_categ_unit')
        cls.uom_unit = cls.env['product.uom'].create({
            'name': 'Test-Unit',
            'category_id': categ_unit.id,
            'rounding': 1.0,
        })
        cls.supplier = cls.env['res.partner'].create({
            'name': 'Supplier',
            'supplier': True,
        })
        picking_type_in = cls.env.ref('stock.picking_type_in')
        cls.supplier_location = cls.env.ref('stock.stock_location_suppliers')
        cls.stock_location = cls.env.ref('stock.stock_location_stock')
        cls.picking = cls.env['stock.picking'].create({
            'picking_type_id': picking_type_in.id,
            'location_id': cls.supplier_location.id,
            'location_dest_id': cls.stock_location.id,
            'partner_id': cls.supplier.id,
            'move_lines': [(0, 0, {
                'product_id': cls.product.id,
                'product_uom_qty': 5.0,
                'name': cls.product.name,
                'product_uom': cls.uom_unit.id,
            })]
        })
        user_type = cls.env.ref('account.data_account_type_expenses')
        account = cls.env['account.account'].create({
            'name': 'Account',
            'code': 'CODE',
            'user_type_id': user_type.id,
        })
        cls.invoice = cls.env['account.invoice'].create({
            'partner_id': cls.supplier.id,
            'type': 'in_invoice',
            'invoice_line_ids': [(0, 0, {
                'product_id': cls.service.id,
                'name': cls.service.name,
                'account_id': account.id,
                'price_unit': cls.service.standard_price,
            })]
        })

    def test_distribution_without_lines(self):
        self.assertNotEqual(self.distribution.name, '/')
        with self.assertRaises(UserError):
            self.distribution.action_calculate()
        self.assertEqual(self.distribution.state, 'draft')

    def test_distribution_import_shipment(self):
        self.picking.action_confirm()
        self.picking.action_assign()
        self.env['stock.move.line'].create({
            'product_id': self.product.id,
            'qty_done': 5,
            'product_uom_id': self.uom_unit.id,
            'location_id': self.supplier_location.id,
            'location_dest_id': self.stock_location.id,
            'move_id': self.picking.move_lines[:1].id,
        })
        self.picking.action_done()
        self.assertEqual(self.picking.state, 'done')
        wiz = self.env['picking.import.wizard'].with_context(
            active_id=self.distribution.id).create({
                'supplier': self.supplier.id,
                'pickings': [(6, 0, [self.picking.id])],
            })
        wiz.action_import_picking()
        self.assertEqual(len(self.distribution.cost_lines.ids), 1)
        self.assertAlmostEqual(self.distribution.total_uom_qty, 5.0)
        self.assertAlmostEqual(self.distribution.amount_total, 15.0)
        self.assertEqual(self.invoice.state, 'draft')
        self.invoice.action_invoice_open()
        self.assertEqual(self.invoice.state, 'open')
        wiz = self.env['import.invoice.line.wizard'].with_context(
            active_id=self.distribution.id).create({
                'supplier': self.supplier.id,
                'invoice': self.invoice.id,
                'invoice_line': self.invoice.invoice_line_ids[:1].id,
                'expense_type': self.type_amount.id,
        })
        wiz.action_import_invoice_line()
        self.assertEqual(len(self.distribution.expense_lines.ids), 1)
        self.assertAlmostEqual(self.distribution.total_uom_qty, 5.0)
        self.assertAlmostEqual(self.distribution.amount_total, 25.0)
        self.distribution.action_calculate()
        self.assertAlmostEqual(self.distribution.total_expense, 10.0)
        self.assertEqual(self.distribution.state, 'calculated')
        self.assertAlmostEqual(self.product.standard_price, 3.0)
        self.distribution.action_done()
        self.assertEqual(self.distribution.state, 'done')
        self.assertAlmostEqual(self.product.standard_price, 4.0)
        self.product.standard_price = 3.0
        self.distribution.action_cancel()
