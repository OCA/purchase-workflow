# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta
from odoo import fields
from odoo.fields import first
from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError


class TestDatePlannedManual(TransactionCase):

    def setUp(self):
        super(TestDatePlannedManual, self).setUp()
        self.po_model = self.env['purchase.order']
        self.pol_model = self.env['purchase.order.line']
        self.pp_model = self.env['product.product']
        # Create some partner, products and supplier info:
        self.route_buy_id = self.env.ref('purchase.route_warehouse0_buy')
        self.rule = first(self.route_buy_id.pull_ids)
        self.partner = self.env['res.partner'].create({
            'name': 'Test supplier',
            'supplier': True,
        })
        supplier_info_id = self.env['product.supplierinfo'].create({
            'name': self.partner.id,
            'delay': 2,
        }).id
        self.product_1 = self.pp_model.create({
            'name': 'Test product 1',
            'type': 'product',
            'route_ids': [(4, self.route_buy_id.id)],
            'seller_ids': [(4, supplier_info_id)],
        })
        self.product_2 = self.pp_model.create({
            'name': 'Test product 2',
            'type': 'product',
        })
        # Create purchase order and dates
        self.purchase_order = self.po_model.create({
            'partner_id': self.partner.id,
            'picking_type_id': self.rule.picking_type_id.id,
        })
        next_week_time = datetime.now() + timedelta(days=7)
        self.next_week_time = fields.Datetime.to_string(next_week_time)

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

    def test_merging_of_po_lines_if_same_date_planned(self):
        """When only merge PO lines if they have same date_planned"""
        po_line_1 = self.pol_model.create({
            'order_id': self.purchase_order.id,
            'product_id': self.product_1.id,
            'date_planned': self.next_week_time,
            'name': 'Test',
            'product_qty': 1.0,
            'product_uom': self.product_1.uom_id.id,
            'price_unit': 10.0,
        })
        # case 1: run procurement - same date_planned (expected merge)
        self.env['procurement.group'].run(
            product_id=self.product_1,
            product_qty=1.0,
            product_uom=self.product_1.uom_id,
            location_id=self.rule.location_id,
            name='/',
            origin='/',
            values={
                'warehouse_id': self.rule.warehouse_id,
                'priority': 1,
                'date_planned': self.next_week_time,
                'company_id': po_line_1.company_id,
            },
        )
        self.assertEqual(len(self.purchase_order.order_line), 1,
                         "The PO should still have only one PO line.")
        self.assertEqual(po_line_1.product_qty, 2.0,
                         "The qty of the PO line should have increased by 1.")
        self.assertEqual(po_line_1.date_planned, self.next_week_time,
                         "The date_planned of the PO line should be the same.")
        # case 2: run procurement - different date_planned (new PO line)
        self.env['procurement.group'].run(
            product_id=self.product_1,
            product_qty=1.0,
            product_uom=self.product_1.uom_id,
            location_id=self.rule.location_id,
            name='/',
            origin='/',
            values={
                'warehouse_id': self.rule.warehouse_id,
                'priority': 1,
                'company_id': po_line_1.company_id,
            },
        )
        self.assertEqual(po_line_1.product_qty, 2.0,
                         "The first PO line product qty should still be 2.")
        self.assertEqual(len(self.purchase_order.order_line), 2,
                         "A new PO line should have been create for the move.")
        self.assertEqual(po_line_1.date_planned, self.next_week_time,
                         "The date_planned of the PO line should be the same.")
        self.assertEqual(
            (self.purchase_order.order_line - po_line_1).date_planned,
            self.purchase_order.date_planned,
            "The date_planned of the PO line should be the same.")
