# -*- coding: utf-8 -*-
#    Author: Yannick Vaucher, Leonardo Pistone
#    Copyright 2014-2015 Camptocamp SA
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

from openerp.tests import common
from openerp import fields


class TestAddresses(common.TransactionCase):

    def setUp(self):
        super(TestAddresses, self).setUp()

        model_data = self.env['ir.model.data']
        ref = model_data.xmlid_to_res_id
        self.part1_id = ref('base.res_partner_1')
        self.part12_id = ref('base.res_partner_12')
        PO = self.env['purchase.order']
        POL = self.env['purchase.order.line']

        po_vals = {
            'partner_id': self.part1_id,
            'location_id': ref('stock.stock_location_stock')
        }

        res = PO.onchange_partner_id(self.part1_id)
        po_vals.update(res['value'])
        self.po = PO.create(po_vals)

        POL.create({
            'order_id': self.po.id,
            'product_id': ref('product.product_product_33'),
            'name': "[HEAD-USB] Headset USB",
            'product_qty': 24,
            'product_uom': ref('product.product_uom_unit'),
            'date_planned': fields.Datetime.now(),
            'price_unit': 65,
        })

    def test_propagate_empty_address_to_picking(self):
        self.po.signal_workflow('purchase_confirm')
        self.assertFalse(self.po.picking_ids.delivery_address_id.id)

    def test_propagate_supplier_and_chosen_address_to_picking(self):
        self.po.dest_address_id = self.part12_id
        self.po.signal_workflow('purchase_confirm')
        self.assertEquals(self.po.picking_ids.delivery_address_id,
                          self.po.dest_address_id)
        self.assertEquals(self.po.picking_ids.partner_id,
                          self.po.partner_id)

    def test_create_picking_with_default_origin(self):
        """Create a picking in from purchase order and check
        origin address is copied

        """

        self.po.signal_workflow('purchase_confirm')
        self.assertTrue(self.po.origin_address_id)
        self.assertEquals(self.po.picking_ids.origin_address_id,
                          self.po.origin_address_id)

    def test_create_picking_without_origin(self):
        """Create a picking in from purchase order
        remove origin address and check
        origin address is false on picking

        """

        self.po.origin_address_id = False
        self.po.signal_workflow('purchase_confirm')
        self.assertFalse(self.po.picking_ids.origin_address_id.id)

    def test_create_picking_with_other_origin(self):
        """Create a picking in from purchase order and check
        origin address is copied and is the same as on the purchase
        order

        """

        self.po.origin_address_id = self.part12_id
        self.po.signal_workflow('purchase_confirm')
        self.assertEquals(self.po.picking_ids.origin_address_id,
                          self.po.origin_address_id)
