
from odoo.tests.common import TransactionCase
from odoo import fields


class PurchaseOrder(TransactionCase):

    def setUp(self):
        super(PurchaseOrder, self).setUp()
        self.product_model = self.env['product.template']
        self.product_template_on_weight = self.product_model.create({
            'name': 'Product on weight',
            'type': 'product',
            'uom_id': self.env.ref('uom.product_uom_meter').id,
            'uom_po_id': self.env.ref('uom.product_uom_meter').id,
            'list_price': 50.0,
            'taxes_id': [(6, 0, self.env['account.tax'].search(
                [('type_tax_use', '=', 'sale')], limit=1).ids)],
            'supplier_taxes_id': [(6, 0, self.env['account.tax'].search(
                [('type_tax_use', '=', 'purchase')], limit=1).ids)],
            'compute_price_on_weight': True,
            'weight': 0.15,
            'seller_ids': [
                (0, 0, {
                    'name': self.env.ref('base.res_partner_3').id,
                    'price': 5.0,
                    'min_qty': 0.0,
                })
            ]
        })
        self.product_on_weight = self.env['product.product'].search([
            ('product_tmpl_id', '=', self.product_template_on_weight.id)
        ], limit=1)

    def test_purchase_order_on_weight(self):
        purchase_order = self.env['purchase.order'].create({
            'partner_id': self.env.ref('base.res_partner_3').id,
            'date_order': fields.Date.today(),
            'order_line': [
                (0, 0, {
                    'product_id': self.product_on_weight.id,
                    'product_qty': 20,
                    'product_uom': self.product_on_weight.uom_po_id.id,
                    'price_unit': self.product_on_weight.list_price,
                    'name': self.product_on_weight.name,
                    'date_planned': fields.Date.today(),
                }),
            ]
        })

        purchase_order.order_line[0]._onchange_quantity()
        self.assertEqual(
            len(purchase_order.order_line), 1, msg="Order line was not created")
        self.assertAlmostEqual(purchase_order.order_line[0].price_unit, 5 * 0.15)
        self.assertAlmostEqual(purchase_order.order_line[0].weight_total, 20 * 0.15)
        purchase_order.order_line[0].product_qty = 25
        purchase_order.order_line[0]._onchange_quantity()
        self.assertAlmostEqual(purchase_order.order_line[0].price_unit, 5 * 0.15)
        self.assertAlmostEqual(purchase_order.order_line[0].weight_total, 25 * 0.15)
