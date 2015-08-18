# -*- coding: utf-8 -*-
# (c) 2015 Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp.tests.common import TransactionCase


class TestProcurementPurchaseNoGrouping(TransactionCase):

    def setUp(self):
        super(TestProcurementPurchaseNoGrouping, self).setUp()
        self.category = self.env['product.category'].create(
            {'name': 'Test category'})
        self.product = self.env['product.product'].create(
            {'name': 'Test product',
             'categ_id': self.category.id,
             'seller_ids': [
                 (0, 0, {'name': self.env.ref('base.res_partner_1').id,
                         'min_qty': 1.0})]}
        )
        self.procurement_1 = self.env['procurement.order'].create(
            {'name': 'Procurement test',
             'product_id': self.product.id,
             'product_uom': self.product.uom_id.id,
             'warehouse_id': self.env.ref('stock.warehouse0').id,
             'location_id': self.env.ref('stock.stock_location_stock').id,
             'route_ids': [
                 (6, 0, [self.env.ref('purchase.route_warehouse0_buy').id])],
             'product_qty': 1.0}
        )
        self.procurement_2 = self.procurement_1.copy()

    def test_procurement_grouped_purchase(self):
        self.category.procured_purchase_grouping = 'standard'
        self.procurement_1.run()
        self.procurement_2.run()
        self.assertTrue(self.procurement_1.purchase_id)
        self.assertTrue(self.procurement_2.purchase_id)
        self.assertEqual(
            self.procurement_1.purchase_id,
            self.procurement_2.purchase_id,
            'Procured purchase orders are not the same')
        self.assertEqual(
            self.procurement_1.purchase_line_id,
            self.procurement_2.purchase_line_id,
            'Procured purchase orders lines are not the same')
        return True

    def test_procurement_no_grouping_line_purchase(self):
        self.category.procured_purchase_grouping = 'line'
        self.procurement_1.run()
        self.procurement_2.run()
        self.assertTrue(self.procurement_1.purchase_id)
        self.assertTrue(self.procurement_2.purchase_id)
        self.assertEqual(
            self.procurement_1.purchase_id,
            self.procurement_2.purchase_id,
            'Procured purchase orders are not the same')
        self.assertNotEqual(
            self.procurement_1.purchase_line_id,
            self.procurement_2.purchase_line_id,
            'Procured purchase orders lines are the same')
        return True

    def test_procurement_no_grouping_order_purchase(self):
        self.category.procured_purchase_grouping = 'order'
        self.procurement_1.run()
        self.procurement_2.run()
        self.assertTrue(self.procurement_1.purchase_id)
        self.assertTrue(self.procurement_2.purchase_id)
        self.assertNotEqual(
            self.procurement_1.purchase_id,
            self.procurement_2.purchase_id,
            'Procured purchase orders are the same')
        self.assertNotEqual(
            self.procurement_1.purchase_line_id,
            self.procurement_2.purchase_line_id,
            'Procured purchase orders lines are the same')
        return True
