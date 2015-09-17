# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015
#    Francesco OpenCode Apruzzese (<f.apruzzese@apuliasoftware.it>)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


import openerp.tests.common as common
from openerp import fields


class TestPurchaseSecondaryUom(common.TransactionCase):

    def setUp(self):
        super(TestPurchaseSecondaryUom, self).setUp()
        # ----- models
        self.purchase_model = self.env['purchase.order']
        self.purchase_line_model = self.env['purchase.order.line']
        # ----- demo datas
        self.partner = self.env.ref('base.res_partner_1')
        self.location = self.env.ref('stock.stock_location_suppliers')
        self.picking_type = self.env.ref('stock.picking_type_in')
        self.pricelist = self.env.ref('purchase.list0')
        self.product = self.env.ref('product.product_product_31')
        self.uom_kg = self.env.ref('product.product_uom_kgm')

    def test_purchase_last_price_info_new_order(self):
        # ----- set units of measure on product
        self.product.uop_id = self.uom_kg.id
        self.product.uop_coeff = 2.0
        self.product.uop_type = 'fixed'
        # ----- Create purchase order
        purchase_order = self.purchase_model.create({
            'partner_id': self.partner.id,
            'location_id': self.location.id,
            'picking_type_id': self.picking_type.id,
            'pricelist_id': self.pricelist.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'price_unit': self.product.standard_price,
                'name': self.product.name,
                'product_qty': 10.0,
                'product_uop_id': self.uom_kg.id,
                'product_uop_qty': 20.0,
                'date_planned': fields.Datetime.now(),
                })]
            })
        # ----- Confirm order and create picking
        purchase_order.wkf_confirm_order()
        purchase_order.action_picking_create()
        # ----- Check quantity on stock move
        self.assertEqual(
            purchase_order.order_line[0].product_uop_id.id,
            purchase_order.order_line[0].move_ids[0].product_uos.id)
        self.assertEqual(
            purchase_order.order_line[0].product_uop_qty,
            purchase_order.order_line[0].move_ids[0].product_uos_qty)
