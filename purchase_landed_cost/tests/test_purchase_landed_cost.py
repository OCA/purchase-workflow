# Copyright 2018 Tecnativa - Vicent Cubells
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.exceptions import UserError
from odoo.tests import common
from odoo import fields


class TestPurchaseLandedCost(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestPurchaseLandedCost, cls).setUpClass()
        expense_type_obj = cls.env['purchase.expense.type']
        cls.type_amount = expense_type_obj.create({
            'name': 'Type Amount',
            'calculation_method': 'amount',
            'default_amount': True,
        })
        cls.type_price = expense_type_obj.create({
            'name': 'Type Price',
            'calculation_method': 'price',
        })
        cls.type_qty = expense_type_obj.create({
            'name': 'Type Qty',
            'calculation_method': 'qty',
        })
        cls.type_weight = expense_type_obj.create({
            'name': 'Type Weight',
            'calculation_method': 'weight',
        })
        cls.type_volume = expense_type_obj.create({
            'name': 'Type Volume',
            'calculation_method': 'volume',
        })
        cls.type_equal = expense_type_obj.create({
            'name': 'Type Equal',
            'calculation_method': 'equal',
        })
        cls.distribution = cls.env['purchase.cost.distribution'].create({
            'name': '/',
        })
        cls.product = cls.env['product.product'].create({
            'name': 'Product',
            'type': 'product',
            'property_cost_method': 'average',
        })
        cls.supplier = cls.env['res.partner'].create({
            'name': 'Supplier',
            'supplier': True,
        })
        cls.purchase_order = cls.env['purchase.order'].create({
            'partner_id': cls.supplier.id,
            'order_line': [(0, 0, {
                'product_id': cls.product.id,
                'product_qty': 5.0,
                'name': cls.product.name,
                'product_uom': cls.product.uom_id.id,
                'price_unit': 3.0,
                'date_planned': fields.Date.today(),
            })]
        })
        cls.purchase_order.button_confirm()
        cls.picking = cls.purchase_order.picking_ids
        cls.env['stock.immediate.transfer'].create({
            'pick_ids': [(4, cls.picking.id)],
        }).process()
        cls.picking.action_done()
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
                'name': 'Test service',
                'account_id': account.id,
                'price_unit': 10.0,
            })]
        })
        cls.invoice.action_invoice_open()
        wiz = cls.env['import.invoice.line.wizard'].with_context(
            active_id=cls.distribution.id,
        ).create({
            'supplier': cls.supplier.id,
            'invoice': cls.invoice.id,
            'invoice_line': cls.invoice.invoice_line_ids[:1].id,
            'expense_type': cls.type_qty.id,
        })
        wiz.action_import_invoice_line()

    def test_distribution_without_lines(self):
        self.assertNotEqual(self.distribution.name, '/')
        with self.assertRaises(UserError):
            self.distribution.action_calculate()
        self.assertEqual(self.distribution.state, 'draft')

    def test_distribution_import_shipment(self):
        self.assertEqual(self.picking.state, 'done')
        wiz = self.env['picking.import.wizard'].with_context(
            active_id=self.distribution.id,
        ).create({
            'supplier': self.supplier.id,
            'pickings': [(6, 0, self.picking.ids)],
        })
        wiz.action_import_picking()
        self.assertEqual(len(self.distribution.cost_lines.ids), 1)
        self.assertAlmostEqual(self.distribution.total_uom_qty, 5.0)
        self.assertAlmostEqual(self.distribution.total_purchase, 15.0)
        self.assertAlmostEqual(self.distribution.amount_total, 25.0)
        # Expense part
        self.assertEqual(len(self.distribution.expense_lines.ids), 1)
        self.assertAlmostEqual(self.distribution.total_uom_qty, 5.0)
        self.distribution.action_calculate()
        self.assertAlmostEqual(self.distribution.cost_lines[0].cost_ratio, 2)
        self.assertAlmostEqual(self.distribution.total_expense, 10.0)
        self.assertAlmostEqual(self.distribution.cost_lines[0].cost_ratio, 2)
        self.assertEqual(self.distribution.state, 'calculated')
        self.assertAlmostEqual(self.product.standard_price, 3.0)
        self.distribution.action_done()
        self.assertEqual(self.distribution.state, 'done')
        self.assertAlmostEqual(self.product.standard_price, 5.0)
        self.distribution.action_cancel()
        self.assertAlmostEqual(self.product.standard_price, 3.0)

    def test_distribution_two_moves(self):
        order2 = self.purchase_order.copy()
        order2.order_line.price_unit = 2
        order2.button_confirm()
        picking2 = order2.picking_ids
        self.env['stock.immediate.transfer'].create({
            'pick_ids': [(4, picking2.id)],
        }).process()
        picking2.action_done()
        wiz = self.env['picking.import.wizard'].with_context(
            active_id=self.distribution.id,
        ).create({
            'supplier': self.supplier.id,
            'pickings': [(6, 0, (self.picking + picking2).ids)],
        })
        wiz.action_import_picking()
        self.assertEqual(len(self.distribution.cost_lines.ids), 2)
        self.assertAlmostEqual(self.distribution.total_uom_qty, 10.0)
        self.assertAlmostEqual(self.distribution.total_purchase, 25.0)
        self.distribution.action_calculate()
        self.assertAlmostEqual(self.distribution.cost_lines[0].cost_ratio, 1)
        self.assertAlmostEqual(self.product.standard_price, 2.5)
        self.distribution.action_done()
        self.assertAlmostEqual(self.product.standard_price, 3.5)
        self.assertAlmostEqual(self.picking.move_lines.price_unit, 4)
        self.assertAlmostEqual(self.picking.move_lines.value, 20)
        self.assertAlmostEqual(picking2.move_lines.price_unit, 3)
        self.assertAlmostEqual(picking2.move_lines.value, 15)
        self.distribution.action_cancel()
        self.assertAlmostEqual(self.product.standard_price, 2.5)

    def test_distribution_two_moves_existing_stock(self):
        order2 = self.purchase_order.copy()
        order2.order_line.price_unit = 2
        order2.button_confirm()
        picking2 = order2.picking_ids
        order3 = self.purchase_order.copy()
        order3.order_line.price_unit = 1
        order3.button_confirm()
        picking3 = order3.picking_ids
        self.env['stock.immediate.transfer'].create({
            'pick_ids': [(6, 0, (picking2 + picking3).ids)],
        }).process()
        (picking2 + picking3).action_done()
        wiz = self.env['picking.import.wizard'].with_context(
            active_id=self.distribution.id,
        ).create({
            'supplier': self.supplier.id,
            'pickings': [(6, 0, (picking2 + picking3).ids)],
        })
        wiz.action_import_picking()
        self.assertAlmostEqual(self.distribution.total_uom_qty, 10.0)
        self.assertAlmostEqual(self.distribution.total_purchase, 15.0)
        self.distribution.action_calculate()
        self.assertAlmostEqual(self.distribution.cost_lines[0].cost_ratio, 1)
        self.assertAlmostEqual(self.product.standard_price, 2)
        self.distribution.action_done()
        self.assertAlmostEqual(self.product.standard_price, 2.67, 2)
        self.distribution.action_cancel()
        self.assertAlmostEqual(self.product.standard_price, 2)
