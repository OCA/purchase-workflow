# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo.tests import common
from .. import hooks


class TestProcurementRunBuyHook(common.TransactionCase):

    def setUp(self):
        super(TestProcurementRunBuyHook, self).setUp()

        # common models
        self.stock_warehouse_orderpoint_model = \
            self.env['stock.warehouse.orderpoint']

        # refs
        self.stock_user_group = \
            self.env.ref('stock.group_stock_user')
        self.main_company = self.env.ref('base.main_company')
        self.warehouse = self.env.ref('stock.warehouse0')
        self.categ_unit = self.env.ref('product.product_uom_categ_unit')

        # common data
        self.stock_user = self._create_user(
            'stock_user',
            [self.stock_user_group.id],
            [self.main_company.id])
        self.route_buy = self.warehouse.buy_pull_id.route_id
        self.supplier = self.env['res.partner'].create({
            'name': 'Supplier',
            'supplier': True,
        })
        self.product = self._create_product('SH', 'Shoes', False)
        hooks.post_load_hook()

    def _create_user(self, name, group_ids, company_ids):
        return self.env['res.users'].with_context(
            {'no_reset_password': True}).create(
            {'name': name,
             'password': 'demo',
             'login': name,
             'email': '@'.join([name, '@test.com']),
             'groups_id': [(6, 0, group_ids)],
             'company_ids': [(6, 0, company_ids)]
             })

    def _create_product(self, default_code, name, company_id):
        return self.env['product.product'].create({
            'name': name,
            'default_code': default_code,
            'uom_id': self.env.ref('product.product_uom_unit').id,
            'company_id': company_id,
            'type': 'product',
            'route_ids': [(6, 0, self.route_buy.ids)],
            'seller_ids': [(0, 0, {'name': self.supplier.id, 'delay': 5})]
        })

    def test_orderpoint_01(self):
        """Orderpoint"""
        vals = {
            'product_id': self.product.id,
            'product_uom': self.product.uom_id.id,
            'product_min_qty': 10,
            'product_max_qty': 100,
            'company_id': self.main_company.id,
            'warehouse_id': self.warehouse.id,
            'location_id': self.warehouse.lot_stock_id.id,
        }

        orderpoint = self.stock_warehouse_orderpoint_model.sudo().create(vals)
        self.env['procurement.group'].run_scheduler()
        po_line = self.env['purchase.order.line'].search(
            [('orderpoint_id', '=', orderpoint.id)], limit=1)
        self.assertEqual(len(po_line), 1)
        self.assertEqual(po_line.product_qty, 100)
        orderpoint.product_min_qty = 200
        orderpoint.product_min_qty = 400
        self.env['procurement.group'].run_scheduler()
        self.assertEqual(po_line.product_qty, 400)
