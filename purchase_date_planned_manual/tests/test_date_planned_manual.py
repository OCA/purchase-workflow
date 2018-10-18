# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta
from odoo import fields
from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError


class TestDatePlannedManual(TransactionCase):
    def setUp(self, *args, **kwargs):
        super(TestDatePlannedManual, self).setUp(*args, **kwargs)
        self.po_model = self.env['purchase.order']
        self.pol_model = self.env['purchase.order.line']
        self.pp_model = self.env['product.product']
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
        self.product_1 = self.pp_model.create({
            'name': 'Test product 1',
            'type': 'product',
            'route_ids': [(4, route_buy_id)],
            'seller_ids': [(4, supplier_info_id)],
        })
        self.product_2 = self.pp_model.create({
            'name': 'Test product 2',
            'type': 'product',
        })
        # Create purchase order and dates
        self.purchase_order = self.po_model.create({
            'partner_id': self.partner.id,
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
