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


class test_cancel_purchase_requisition(common.TransactionCase):
    """ Test the cancellation of purchase requisition and ensure that related
    Purchase Orders/Request For Quotation are cancelled
    """

    def setUp(self):
        super(test_cancel_purchase_requisition, self).setUp()
        PReq = self.env['purchase.requisition']
        PO = self.env['purchase.order']

        self.preq = PReq.new({'state': 'draft'})

        self.po_sent = PO.new({'state': 'draft'})
        self.po_draft = PO.new({'state': 'sent'})

    def test_cancel_draft_purchase_requisition(self):
        """ We cancel a draft purchase requisition
        """
        self.preq.tender_cancel()
        self.assertEqual(self.preq.state, 'cancel')

    def test_cancel_in_progress_purchase_requisition_without_bid(self):
        """ We cancel a confirmed purchase requisition without Bid
        """
        self.preq.tender_cancel()
        self.assertEqual(self.preq.state, 'cancel')

    def test_cancel_in_progress_purchase_requisition_with_1draft_rfq(self):
        """ We cancel a confirmed purchase requisition with 1 RFQ in
        draft state
        """
        self.preq.state = 'in_progress'
        self.purchase_ids = self.po_draft
        self.preq.tender_cancel()
        for po in self.preq.purchase_ids:
            self.assertEquals(po.state, 'cancel')

    def test_cancel_in_progress_purchase_requisition_with_1sent_rqf(self):
        """ We cancel a confirmed purchase requisition with 1 RFQ
        in sent state
        """
        self.preq.state = 'in_progress'
        self.purchase_ids = self.po_sent
        self.preq.tender_cancel()
        self.assertEqual(self.preq.state, 'cancel')
        for po in self.preq.purchase_ids:
            self.assertEquals(po.state, 'cancel')

    def test_cancel_in_progress_purchase_requisition_with_2bids(self):
        """ We cancel a confirmed purchase requisition with 2 RFQ
        """
        purchases = self.env['purchase.order']
        purchases |= self.po_draft
        purchases |= self.po_sent
        self.preq.state = 'in_progress'
        self.preq.tender_cancel()
        self.assertEqual(self.preq.state, 'cancel')
        for po in self.preq.purchase_ids:
            self.assertEquals(po.state, 'cancel')
