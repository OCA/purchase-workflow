# -*- coding: utf-8 -*-
#
#
#    Copyright 2013, 2014 Camptocamp SA
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
from openerp import models, api


class PurchaseRequisitionPartner(models.TransientModel):
    _inherit = "purchase.requisition.partner"

    @api.multi
    def create_order(self):
        ActWindow = self.env['ir.actions.act_window']
        Requisition = self.env['purchase.requisition']
        active_id = self.env.context and self.env.context.get('active_id', [])

        requisition = Requisition.browse(active_id)

        po_id = requisition.make_purchase_order(self.partner_id.id)[active_id]

        if not self.env.context.get('draft_bid', False):
            return {'type': 'ir.actions.act_window_close'}
        res = ActWindow.for_xml_id('purchase', 'purchase_rfq')
        res.update({'res_id': po_id,
                    'views': [(False, 'form')],
                    })
        return res
