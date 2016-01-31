# -*- coding: utf-8 -*-
# (c) 2015 Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp.tests.common import TransactionCase


class TestProcurementPurchaseNoGrouping(TransactionCase):

    def _make_procurements(self, procured_purchase_grouping):
        category = self.env['product.category'].create({
            'name': 'Test category %s' % procured_purchase_grouping,
            'procured_purchase_grouping': procured_purchase_grouping,
        })
        product = self.env['product.product'].create({
            'name': 'Test product',
            'categ_id': category.id,
            'seller_ids': [(0, 0, {
                'name': self.env.ref('base.res_partner_1').id,
                'min_qty': 1.0,
            })],
        })
        procurement_1 = self.env['procurement.order'].create({
            'name': 'Procurement test',
            'product_id': product.id,
            'product_uom': product.uom_id.id,
            'warehouse_id': self.env.ref('stock.warehouse0').id,
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'route_ids': [(6, 0, [
                self.env.ref('purchase.route_warehouse0_buy').id
            ])],
            'product_qty': 1.0,
        })
        procurement_2 = procurement_1.copy()
        return (procurement_1, procurement_2)

    def test_procurement_grouped_purchase(self):
        procurement_1, procurement_2 = self._make_procurements('standard')
        procurement_1.run()
        procurement_2.run()
        self.assertTrue(procurement_1.purchase_id)
        self.assertTrue(procurement_2.purchase_id)
        self.assertEqual(
            procurement_1.purchase_id,
            procurement_2.purchase_id,
            'Procured purchase orders are not the same')
        self.assertEqual(
            procurement_1.purchase_line_id,
            procurement_2.purchase_line_id,
            'Procured purchase orders lines are not the same')
        return True

    def test_procurement_no_grouping_line_purchase(self):
        procurement_1, procurement_2 = self._make_procurements('line')
        procurement_1.run()
        procurement_2.run()
        self.assertTrue(procurement_1.purchase_id)
        self.assertTrue(procurement_2.purchase_id)
        self.assertEqual(
            procurement_1.purchase_id,
            procurement_2.purchase_id,
            'Procured purchase orders are not the same')
        self.assertNotEqual(
            procurement_1.purchase_line_id,
            procurement_2.purchase_line_id,
            'Procured purchase orders lines are the same')
        return True

    def test_procurement_no_grouping_order_purchase(self):
        procurement_1, procurement_2 = self._make_procurements('order')
        procurement_1.run()
        procurement_2.run()
        self.assertTrue(procurement_1.purchase_id)
        self.assertTrue(procurement_2.purchase_id)
        self.assertNotEqual(
            procurement_1.purchase_id,
            procurement_2.purchase_id,
            'Procured purchase orders are the same')
        self.assertNotEqual(
            procurement_1.purchase_line_id,
            procurement_2.purchase_line_id,
            'Procured purchase orders lines are the same')
        return True
