# -*- coding: utf-8 -*-
#
#
#    Copyright 2013 Camptocamp SA
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

from openerp import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    bid_partial = fields.Boolean(
        'Bid partially selected',
        readonly=True,
        help="True if the bid has been partially selected")
    tender_bid_receipt_mode = fields.Selection(
        compute='_get_tender',
        multi="callforbids",
        readonly=True,
        type='selection',
        selection=[('open', 'Open'), ('sealed', 'Sealed')],
        string='Bid Receipt Mode')

    @api.model
    def _get_tender_fields(self):
        """ Return list of field with prefix 'tender_' """
        return [fname for fname in self._fields.keys()
                if fname.startswith('tender_')]
    @api.model
    def _get_fields_to_copy(self):
        """ Return list of field that have an existing field with prefix
        'tender_'
        """
        return [fname[len('tender_'):] for fname in self._get_tender_fields()]

    #TODO: lines should not be deleted or created if linked to a callforbids

    @api.multi
    def _get_tender(self):
        requisitions = [order.requisition_id for order in self
                        if order.requisition_id]
        # we'll read the fields without the 'tender_' prefix
        # and copy their value in the fields with the prefix
        fields_to_copy = self._get_tender_fields()
        tender_vals = requisitions.read(fields_to_copy,
                                        load='_classic_write')
        # copy the dict but rename the fields with 'tender_' prefix
        tender_reqs = {}
        for req in tender_vals:
            tender_reqs[req['id']] = dict(('tender_' + field, value)
                                          for field, value
                                          in req.iteritems()
                                          if field in fields_to_copy)
        res = {}
        for order in self:
            if order.requisition_id:
                res[order.id] = tender_reqs[order.requisition_id.id]
            else:
                res[order.id] = {}.fromkeys(fields_to_copy, False)
        return res

    @api.model
    def _prepare_purchase_order(self, requisition, supplier):
        values = super(PurchaseOrder, self
                       )._prepare_purchase_order(requisition, supplier)
        values.update({
            'bid_validity': requisition.req_validity,
            'payment_term_id': requisition.req_payment_term_id,
            'incoterm_id': requisition.req_incoterm_id,
            'incoterm_address': requisition.req_incoterm_address,
            'transport_mode_id': requisition.req_transport_mode_id,
        })
        if requisition.pricelist_id:
            values.update({'pricelist_id': requisition.pricelist_id.id})
        return values

    @api.one
    def copy(self, default=None):
        """ Need to set origin after copy because original copy clears origin

        """
        if default is None:
            default = {}
        initial_origin = default.get('origin')
        newid = super(PurchaseOrder, self).copy(default=default)
        if initial_origin and 'requisition_id' in default:
            self.sudo().write([newid], {'origin': initial_origin})
        return newid


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    requisition_line_id = fields.Many2one(
        'purchase.requisition.line', 'Call for Bid Line', readonly=True),

    @api.model
    def read_group(self, domain, fields, groupby, offset=0,
                   limit=None, orderby=False):
        """Do not aggregate price and qty. We need to do it this way as there
        is no group_operator that can be set to prevent aggregating float"""
        result = super(PurchaseOrderLine, self
                       ).read_group(domain, fields, groupby,
                                    offset=offset, limit=limit,
                                    orderby=orderby)
        for res in result:
            if 'price_unit' in res:
                del res['price_unit']
            if 'product_qty' in res:
                del res['product_qty']
            if 'lead_time' in res:
                del res['lead_time']
        return result
