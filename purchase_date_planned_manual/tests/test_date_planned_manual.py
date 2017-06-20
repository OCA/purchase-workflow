# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase
from openerp import fields
from datetime import timedelta, datetime
from openerp.exceptions import UserError


class SomethingCase(TransactionCase):
    def setUp(self, *args, **kwargs):
        super(SomethingCase, self).setUp(*args, **kwargs)
        self.po_model = self.env['purchase.order']
        self.pol_model = self.env['purchase.order.line']
        self.proc_model = self.env['procurement.order']
        # Create some partner, products and supplier info:
        route_buy_id = self.env.ref('purchase.route_warehouse0_buy').id
        self.partner = self.env['res.partner'].create({
            'name': 'Test supplier',
            'supplier': True,
        })
        supplier_info_id = self.env['product.supplierinfo'].create({
            'name': self.partner.id,
            'delay': 2,
        }).id
        self.product_1 = self.env['product.product'].create({
            'name': 'Test product 1',
            'type': 'product',
            'route_ids': [(4, route_buy_id)],
            'seller_ids': [(4, supplier_info_id)],
        })
        self.product_2 = self.env['product.product'].create({
            'name': 'Test product 2',
            'type': 'product',
        })
        # Create purchase order and dates
        self.purchase_order = self.env['purchase.order'].create({
            'partner_id': self.partner.id,
        })
        next_week_time = datetime.now() + timedelta(days=7)
        self.next_week_time = fields.Datetime.to_string(next_week_time)
        # Create a warehouse
        self.test_warehouse = self.env['stock.warehouse'].create({
            'name': 'Test Warehouse',
            'code': 'T-WH',
        })
        self.test_location = self.test_warehouse.lot_stock_id

    def test_manually_set_pol_date(self):
        """Tests the manual modification of scheduled date in purchase order
        lines."""
        last_week_time = datetime.now() - timedelta(days=7)
        last_week_time = fields.Datetime.to_string(last_week_time)
        po_line_1 = self.pol_model.create({
            'order_id': self.purchase_order.id,
            'product_id': self.product_1.id,
            'date_planned': last_week_time,
            'name': 'Test',
            'product_qty': 1.0,
            'product_uom': self.product_1.uom_id.id,
            'price_unit': 10.0,
        })
        po_line_2 = self.pol_model.create({
            'order_id': self.purchase_order.id,
            'product_id': self.product_2.id,
            'date_planned': self.next_week_time,
            'name': 'Test',
            'product_qty': 10.0,
            'product_uom': self.product_2.uom_id.id,
            'price_unit': 20.0,
        })
        self.assertTrue(po_line_1.predicted_arrival_late,
                        "First test PO line should be predicted late.")
        self.assertFalse(po_line_2.predicted_arrival_late,
                         "Second test PO line should not be predicted late.")
        self.purchase_order.button_confirm()
        self.assertEqual(po_line_1.date_planned, last_week_time,
                         "Scheduled date should have benn respected.")
        self.assertFalse(po_line_1.predicted_arrival_late,
                         "prediceted_arrival_late should be false when not in "
                         "state 'draft'.")
        with self.assertRaises(UserError):
            po_line_1.action_delayed_line()

    def test_po_created_from_procurements(self):
        """Tests the purchase order lines created from procurement orders."""
        proc = self.proc_model.create({
            'name': 'test',
            'product_id': self.product_1.id,
            'product_qty': 5.0,
            'product_uom': self.product_1.uom_id.id,
            'warehouse_id': self.test_warehouse.id,
            'location_id': self.test_location.id,
            'date_planned': self.next_week_time,
        })
        self.assertEqual(proc.state, 'running',
                         "Procurement has not run correctly.")
        self.assertTrue(proc.purchase_id,
                        "No purchase order created from procurement.")
        pol_date = proc.purchase_id.order_line.date_planned
        self.assertEqual(pol_date, self.next_week_time,
                         "Dates in procurement a purchase order line does not "
                         "match.")
