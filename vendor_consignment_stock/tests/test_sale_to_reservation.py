#    Author: Leonardo Pistone
#    Copyright 2014 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
from openerp.tests.common import TransactionCase


class TestSaleToReservation(TransactionCase):

    def test_sale_vci_generates_procurements_and_special_po(self):
        self.sol.stock_owner_id = self.supplier

        self.so.action_button_confirm()
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
        po.signal_workflow('purchase_confirm')
        self.assertEqual(0, len(po.picking_ids))

        self.Procurement.run_scheduler()
        self.assertEqual('assigned', delivery.state)

    def test_sale_mto_buy_creates_procurements_and_normal_po(self):

        self.product.route_ids = (
            self.env.ref('stock.route_warehouse0_mto') |
            self.env.ref('purchase.route_warehouse0_buy')
        )

        self.so.action_button_confirm()
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
        po.signal_workflow('purchase_confirm')
        self.assertEqual(1, len(po.picking_ids))

    def test_customer_is_owner_reserves_without_po(self):

        self.sol.stock_owner_id = self.customer

        self.so.action_button_confirm()
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
        self.product = self.env.ref('product.product_product_36')
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
