# -*- coding: utf-8 -*-
#
#
#    Author: Yannick Vaucher
#    Copyright 2015 Camptocamp SA
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
import openerp.tests.common as common
from openerp import fields


class test_generate_po(common.TransactionCase):
    """ Test generation of a purchase order from selected Bid and ensure
    unselected Bids are cancelled
    """

    def setUp(self):
        super(test_generate_po, self).setUp()
        PReq = self.env['purchase.requisition']
        PO = self.env['purchase.order']
        POL = self.env['purchase.order.line']

        # Put purchase.requisition directly to 'closed'
        dummy_wkf_trans = self.env['workflow.transition'].create({
            'act_from': self.env.ref('purchase_requisition.act_draft').id,
            'act_to': self.env.ref(
                'purchase_requisition_bid_selection.act_closed').id,
            'condition': True,
        })
        self.preq = PReq.create({'state': 'closed',
                                 'pricelist_id': self.ref('purchase.list0')})
        dummy_wkf_trans.unlink()

        partner_12 = self.env.ref('base.res_partner_12')
        partner_13 = self.env.ref('base.res_partner_13')
        partner_14 = self.env.ref('base.res_partner_14')

        # Put purchase.oders directly to 'bid'
        dummy_wkf_trans = self.env['workflow.transition'].create({
            'act_from': self.env.ref('purchase.act_draft').id,
            'act_to': self.env.ref('purchase.act_bid').id,
            'condition': True,
        })
        self.bid_selected = PO.create(
            {'state': 'bid',
             'bid_partial': True,
             'partner_id': partner_12.id,
             'location_id': self.env.ref('stock.stock_location_stock').id,
             'pricelist_id': partner_12.property_product_pricelist_purchase.id,
             })
        POL.create({
            'state': 'confirmed',
            'order_id': self.bid_selected.id,
            'name': '/',
            'price_unit': 100,
            'date_planned': fields.Datetime.now(),
            })
        self.bid = PO.create(
            {'state': 'bid',
             'partner_id': partner_13.id,
             'location_id': self.env.ref('stock.stock_location_stock').id,
             'pricelist_id': partner_13.property_product_pricelist_purchase.id,
             })
        dummy_wkf_trans.unlink()

        # draftbid is at same workflow state as draft
        self.draftbid = PO.create(
            {'state': 'draftbid',
             'partner_id': partner_14.id,
             'location_id': self.env.ref('stock.stock_location_stock').id,
             'pricelist_id': partner_14.property_product_pricelist_purchase.id,
             })

        purchases = self.bid_selected | self.bid | self.draftbid
        self.preq.purchase_ids = purchases
        self.preq.po_line_ids = purchases.mapped('order_line')

    def test_generate_po(self):
        """ We generate the PO of a Purchase Requisition having 3 Bids in
        different states

        """
        self.preq.generate_po()
        self.assertEqual(self.preq.state, 'done')
        self.assertEqual(self.bid_selected.state, 'bid_selected')
        self.assertEqual(self.bid.state, 'cancel')
        self.assertEqual(self.draftbid.state, 'cancel')
