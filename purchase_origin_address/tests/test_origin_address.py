# -*- coding: utf-8 -*-
#
#
#    Author: Yannick Vaucher
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
#
#
from openerp.tests import common
from openerp import fields


class TestOriginAddress(common.TransactionCase):
    """ Test origin address is correctly set on picking
    """

    def setUp(self):
        super(TestOriginAddress, self).setUp()

        model_data = self.env['ir.model.data']
        self.ref = model_data.xmlid_to_res_id
        self.part1_id = self.ref('base.res_partner_1')
        self.part12_id = self.ref('base.res_partner_12')
        self.order1_vals = {
            'partner_id': self.part1_id,
            'location_id': self.ref('stock.stock_location_stock')
            }

        self.order_line1_vals = {
            'product_id': self.ref('product.product_product_33'),
            'name': "[HEAD-USB] Headset USB",
            'product_qty': 24,
            'product_uom': self.ref('product.product_uom_unit'),
            'date_planned': fields.Datetime.now(),
            'price_unit': 65,
            }

        self.PurchaseOrder = self.env['purchase.order']

    def test_create_picking_with_default_origin(self):
        """Create a picking in from purchase order and check
        origin address is copied

        """

        po_vals = self.order1_vals.copy()
        res = self.PurchaseOrder.onchange_partner_id(self.part1_id)
        po_vals.update(res['value'])

        po1 = self.PurchaseOrder.create(po_vals)

        pol_vals = self.order_line1_vals.copy()
        pol_vals['order_id'] = po1.id
        self.env['purchase.order.line'].create(pol_vals)

        po1.signal_workflow('purchase_confirm')

        self.assertEquals(po1.picking_ids.origin_address_id,
                          po1.origin_address_id)

    def test_create_picking_without_origin(self):
        """Create a picking in from purchase order
        remove origin address and check
        origin address is false on picking

        """

        po_vals = self.order1_vals.copy()
        res = self.PurchaseOrder.onchange_partner_id(self.part1_id)
        po_vals.update(res['value'])

        po2 = self.PurchaseOrder.create(po_vals)

        po2.origin_address_id = False

        pol_vals = self.order_line1_vals.copy()
        pol_vals['order_id'] = po2.id
        self.env['purchase.order.line'].create(pol_vals)

        po2.signal_workflow('purchase_confirm')

        self.assertFalse(po2.picking_ids.origin_address_id.id)

    def test_create_picking_with_other_origin(self):
        """Create a picking in from purchase order and check
        origin address is copied and is the same as on the purchase
        order

        """

        po_vals = self.order1_vals.copy()
        res = self.PurchaseOrder.onchange_partner_id(self.part1_id)
        po_vals.update(res['value'])

        po3 = self.PurchaseOrder.create(po_vals)

        po3.origin_address_id = self.part12_id

        pol_vals = self.order_line1_vals.copy()
        pol_vals['order_id'] = po3.id
        self.env['purchase.order.line'].create(pol_vals)

        po3.signal_workflow('purchase_confirm')

        self.assertEquals(po3.picking_ids.origin_address_id,
                          po3.origin_address_id)
