# -*- coding: utf-8 -*-
# Author: Leonardo Pistone
# Copyright 2014 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime
from odoo.tests.common import TransactionCase
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class TestSaleToReservation(TransactionCase):

    def test_sale_vci_generates_procurements_and_special_po(self):
        self.sol.stock_owner_id = self.supplier

        self.so.action_confirm()
        self.Procurement.run_scheduler()
        delivery = self.so.picking_ids
        self.assertEqual(1, len(delivery))
        self.assertEqual('waiting', delivery.state)

        proc1 = self.sol.procurement_ids
        self.assertEqual(1, len(proc1))
        self.assertEqual("move", proc1.rule_id.action)
        self.assertEqual("make_to_order", proc1.rule_id.procure_method)
        self.assertFalse(proc1.purchase_id)

        proc2 = proc1.group_id.procurement_ids - proc1
        self.assertEqual(1, len(proc2))
        self.assertEqual("buy_vci", proc2.rule_id.action)

        po = proc2.purchase_id
        self.assertTrue(po)
        self.assertIs(True, po.is_vci)
        self.assertEqual(self.supplier, po.partner_id)
        po.button_confirm()
        self.assertEqual(0, len(po.picking_ids))

        self.Procurement.run_scheduler()
        self.assertEqual('assigned', delivery.state)

    def test_sale_mto_buy_creates_procurements_and_normal_po(self):

        self.product.route_ids = (
            self.env.ref('stock.route_warehouse0_mto') |
            self.env.ref('purchase.route_warehouse0_buy')
        )

        self.so.action_confirm()
        self.Procurement.run_scheduler()
        delivery = self.so.picking_ids
        self.assertEqual(1, len(delivery))
        self.assertEqual('waiting', delivery.state)

        proc1 = self.sol.procurement_ids
        self.assertEqual(1, len(proc1))
        self.assertEqual("move", proc1.rule_id.action)
        self.assertEqual("make_to_order", proc1.rule_id.procure_method)
        self.assertFalse(proc1.purchase_id)

        proc2 = proc1.group_id.procurement_ids - proc1
        self.assertEqual(1, len(proc2))
        self.assertEqual("buy", proc2.rule_id.action)

        po = proc2.purchase_id
        self.assertTrue(po)
        self.assertIs(False, po.is_vci)
        date_planned = datetime.strftime(
            datetime.now(), DEFAULT_SERVER_DATETIME_FORMAT)
        for order_line in po.order_line:
            # test compatibility with purchase_delivery_split_date:
            # otherwise, 2 pickings would be generated
            order_line.date_planned = date_planned
        po.button_confirm()
        self.assertEqual(1, len(po.picking_ids))

    def test_customer_is_owner_reserves_without_po(self):

        self.sol.stock_owner_id = self.customer

        self.so.action_confirm()
        self.Procurement.run_scheduler()
        delivery = self.so.picking_ids
        self.assertEqual(1, len(delivery))
        delivery.action_assign()
        self.assertEqual('assigned', delivery.state)

        proc1 = self.sol.procurement_ids
        self.assertEqual(1, len(proc1))
        self.assertEqual("move", proc1.rule_id.action)
        self.assertEqual("make_to_stock", proc1.rule_id.procure_method)
        self.assertFalse(proc1.purchase_id)
        self.assertEqual(1, len(proc1.group_id.procurement_ids))

    def setUp(self):
        super(TestSaleToReservation, self).setUp()
        self.Procurement = self.env['procurement.order']

        self.supplier = self.env.ref('base.res_partner_1')
        self.customer = self.env.ref('base.res_partner_2')
        self.product = self.env.ref('product.product_product_6')
        self.env.ref('stock.warehouse0').buy_vci_to_resupply = True

        our_quant = self.env['stock.quant'].create({
            'qty': 5000,
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'product_id': self.product.id,
        })
        our_quant.copy({
            'owner_id': self.supplier.id,
        })
        our_quant.copy({
            'owner_id': self.customer.id,
        })

        self.so = self.env['sale.order'].create({
            'partner_id': self.customer.id,
            'picking_policy': 'direct',
        })
        self.sol = self.env['sale.order.line'].create({
            'name': '/',
            'order_id': self.so.id,
            'product_id': self.product.id,
        })
