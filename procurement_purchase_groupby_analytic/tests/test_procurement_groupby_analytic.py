# -*- coding: utf-8 -*-
# Copyright 2015 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import odoo.tests.common as common


class TestProcurementGroupbyOrder(common.TransactionCase):

    def setUp(self):
        """ Create a rule to create purchase order from procurement order (buy)
            Set a route to select it form sale order
        """
        super(TestProcurementGroupbyOrder, self).setUp()
        self.buy_route = self.env['stock.location.route'].create(
            {'name': 'Buy route', 'sequence': 1,
             'sale_selectable': True})
        loc_customer_id = self.env.ref('stock.stock_location_customers').id
        loc_supplier_id = self.env.ref('stock.stock_location_suppliers').id
        self.env['procurement.rule'].create({
            'name': 'Buy products',
            'action': 'buy',
            'route_id': self.buy_route.id,
            'location_id': loc_customer_id,
            'location_src_id': loc_supplier_id,
            'picking_type_id': self.env["stock.picking.type"].search([])[0].id,
        })
        self.product = self.env.ref('product.product_product_9')
        self.project = self.env['account.analytic.account'].create({
            'name': 'Account Analytic for Tests'
        })
        self.partner = self.env.ref('base.res_partner_3')

    def test_procurement(self):
        """ Create sale order :
                * product.product_product_9
            Create sale order :
                * product.product_product_9
                * analytic account
            Confirm sale order
            Check there is two po
            Check analytic account is not set on po_line 1
            Check analytic account is analytic account on po_line 2
        """

        so1 = self.env['sale.order'].create(
            {'partner_id': self.partner.id})
        self.env['sale.order.line'].create(
            {'order_id': so1.id,
             'product_id': self.product.id,
             'route_id': self.buy_route.id})
        so2 = self.env['sale.order'].create(
            {'partner_id': self.partner.id,
             'project_id': self.project.id})
        self.env['sale.order.line'].create(
            {'order_id': so2.id,
             'product_id': self.product.id,
             'route_id': self.buy_route.id})

        so1.action_confirm()
        so2.action_confirm()

        po1 = so1.procurement_group_id.procurement_ids.purchase_id
        po2 = so2.procurement_group_id.procurement_ids.purchase_id
        self.assertNotEqual(po1.id, po2.id)
        self.assertFalse(po1.order_line.account_analytic_id)
        self.assertEqual(po2.order_line.account_analytic_id.id,
                         self.project.id)

    def test_procurement_mto(self):
        """ set prodcut.product_product_9 as mto
            Create sale order :
                * product.product_product_9
                * analytic account
            Confirm sale order
            Check there is one po
            Check analytic account is analytic account on po_line
        """
        self.product.route_ids = [(
            4, self.env.ref('stock.route_warehouse0_mto').id)]
        so = self.env['sale.order'].create(
            {'partner_id': self.partner.id,
             'project_id': self.project.id})
        self.env['sale.order.line'].create(
            {'order_id': so.id,
             'product_id': self.product.id,
             'route_id': self.buy_route.id})

        so.action_confirm()

        self.env['procurement.order'].run_scheduler()

        for proc in so.procurement_group_id.procurement_ids:
            if proc.purchase_id:
                po = proc.purchase_id
        self.assertEqual(po.order_line.account_analytic_id.id,
                         self.project.id)

    def test_multi_procurement(self):
        """ set prodcut.product_product_9 as mto
            set product.product_product_11 same supplier
            Create sale order :
                * product.product_product_9
                * product.product_product_11
                * analytic account
            Confirm sale order
            Check there is one po
            Check analytic account is analytic account on po_line
        """
        self.product.route_ids = [(
            4, self.env.ref('stock.route_warehouse0_mto').id)]
        product2 = self.env.ref('product.product_product_11')
        product2.route_ids = [(
            4, self.env.ref('stock.route_warehouse0_mto').id)]
        product2.seller_ids.name = self.product.seller_ids.name
        self.assertEquals(self.product.seller_ids.name,
                          product2.seller_ids.name)
        so = self.env['sale.order'].create(
            {'partner_id': self.partner.id,
             'project_id': self.project.id})
        self.env['sale.order.line'].create(
            {'order_id': so.id,
             'product_id': self.product.id,
             'route_id': self.buy_route.id})
        self.env['sale.order.line'].create(
            {'order_id': so.id,
             'product_id': product2.id,
             'route_id': self.buy_route.id})

        so.action_confirm()

        self.env['procurement.order'].run_scheduler()

        for proc in so.procurement_group_id.procurement_ids:
            if proc.purchase_id:
                po = proc.purchase_id
        self.assertEquals(2, len(po.order_line))
        for po_line in po.order_line:
            self.assertEqual(po_line.account_analytic_id.id,
                             self.project.id)
