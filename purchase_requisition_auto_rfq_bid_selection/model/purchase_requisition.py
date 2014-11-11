# -*- coding: utf-8 -*-
##############################################################################
#
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
##############################################################################
from openerp import models, api


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    @api.multi
    def make_purchase_order(self, seller_id):
        """
        Depending on bid_tendering_mode, generate bids or rfq
        """
        if 'draft_bid' in self.env.context:
            _super = super(PurchaseRequisition, self)
            return _super.make_purchase_order(seller_id)
        res = {}
        requisitions_draft_bid = self.with_context(draft_bid=1).browse()
        requisitions_draft_rfq = self.with_context(draft_bid=0).browse()
        for requisition in self:
            if requisition.bid_tendering_mode == 'restricted':
                requisitions_draft_rfq |= requisition
            else:
                requisitions_draft_bid |= requisition
        for requisitions in (requisitions_draft_bid, requisitions_draft_rfq):
            po_info = requisitions.make_purchase_order(seller_id)
            res.update(po_info)
        return res
