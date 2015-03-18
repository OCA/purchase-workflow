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


class TestConsigneePurchaseOrder(common.TransactionCase):
    """ Test origin address is correctly set on picking
    """

    def setUp(self):
        super(TestConsigneePurchaseOrder, self).setUp()

        model_data = self.env['ir.model.data']
        ref = model_data.xmlid_to_res_id
        self.part1_id = ref('base.res_partner_1')
        self.part12_id = ref('base.res_partner_12')

        PO = self.env['purchase.order']
        POL = self.env['purchase.order.line']

        po_vals = {
            'location_id': ref('stock.stock_location_stock'),
            'partner_id': self.part12_id,
            }

        res = PO.onchange_partner_id(self.part12_id)
        po_vals.update(res['value'])

        self.po = PO.create(po_vals)

        pol_vals = {
            'order_id': self.po.id,
            'product_id': ref('product.product_product_33'),
            'name': "[HEAD-USB] Headset USB",
            'product_qty': 24,
            'product_uom': ref('product.product_uom_unit'),
            'date_planned': fields.Datetime.now(),
            'price_unit': 65,
            }
        POL.create(pol_vals)

    def test_create_picking_with_consignee(self):
        """Create a picking in from purchase order and check
        consignee is copied

        """

        self.po.consignee_id = self.part1_id
        self.po.signal_workflow('purchase_confirm')
        self.assertTrue(self.po.picking_ids)
        self.assertEquals(self.po.picking_ids.consignee_id,
                          self.po.consignee_id)

    def test_create_picking_without_consignee(self):
        """Create a picking in from purchase order
        remove origin address and check
        consignee is false on picking

        """
        self.po.signal_workflow('purchase_confirm')

        self.assertFalse(self.po.picking_ids.consignee_id.id)
