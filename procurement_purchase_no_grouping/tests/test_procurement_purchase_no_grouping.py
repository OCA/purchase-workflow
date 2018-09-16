# Copyright 2015-2017 - Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields
from odoo.tests import common


class TestProcurementPurchaseNoGrouping(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestProcurementPurchaseNoGrouping, cls).setUpClass()
        cls.category = cls.env['product.category'].create({
            'name': 'Test category',
        })
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test partner',
        })
        cls.product = cls.env['product.product'].create({
            'name': 'Test product',
            'categ_id': cls.category.id,
            'seller_ids': [
                (0, 0, {
                    'name': cls.partner.id,
                    'min_qty': 1.0,
                }),
            ]}
        )
        # FIXME: Core doesn't find correctly supplier if this is not set
        cls.product.seller_ids.product_id = cls.product.id
        cls.location = cls.env.ref('stock.stock_location_stock')
        cls.picking_type = cls.env.ref('stock.picking_type_in')
        cls.origin = 'Test procurement_purchase_no_grouping'
        cls.stock_location_route = cls.env.ref('purchase.route_warehouse0_buy')
        cls.procurement_rule = cls.stock_location_route.pull_ids[0]
        cls.values = {
            # FIXME: Core doesn't find correctly supplier if not recordset
            'company_id': cls.env.user.company_id,
            'date_planned': fields.Datetime.now(),
        }

    def _run_procurement(self):
        self.procurement_rule._run_buy(
            self.product, 1, self.product.uom_id, self.location, False,
            self.origin, self.values,
        )

    def test_procurement_grouped_purchase(self):
        self.category.procured_purchase_grouping = 'standard'
        self._run_procurement()
        self._run_procurement()
        orders = self.env['purchase.order'].search([
            ('origin', '=', self.origin),
        ])
        self.assertEqual(
            len(orders), 1, 'Procured purchase orders are not the same',
        )
        self.assertEqual(
            len(orders.order_line), 1,
            'Procured purchase orders lines are not the same',
        )

    def test_procurement_no_grouping_line_purchase(self):
        self.category.procured_purchase_grouping = 'line'
        self._run_procurement()
        self._run_procurement()
        orders = self.env['purchase.order'].search([
            ('origin', '=', self.origin),
        ])
        self.assertEqual(
            len(orders), 1, 'Procured purchase orders are not the same',
        )
        self.assertEqual(
            len(orders.order_line), 2,
            'Procured purchase orders lines are the same',
        )

    def test_procurement_no_grouping_order_purchase(self):
        self.category.procured_purchase_grouping = 'order'
        self._run_procurement()
        self._run_procurement()
        orders = self.env['purchase.order'].search([
            ('origin', '=', self.origin),
        ])
        self.assertEqual(
            len(orders), 2, 'Procured purchase orders are the same',
        )
        self.assertEqual(
            len(orders.mapped('order_line')), 2,
            'Procured purchase orders lines are the same',
        )
