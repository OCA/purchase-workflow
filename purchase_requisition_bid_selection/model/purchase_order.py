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

from openerp import models, fields, api, osv


class PurchaseOrderClassic(osv.orm.Model):
    _inherit = "purchase.order"

    _columns = {
        'tender_bid_receipt_mode': osv.fields.related(
            'requisition_id',
            'bid_receipt_mode',
            type='selection',
            selection=[('open', 'Open'), ('sealed', 'Sealed')],
            string='Bid Receipt Mode'),
    }


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    bid_partial = fields.Boolean(
        'Bid partially selected',
        readonly=True,
        help="True if the bid has been partially selected")
    keep_in_draft = fields.Boolean(
        'Prevent validation of purchase order.',
        help="Technical field used to prevent the PO that is automatically "
        "generated from a Tender to be validated. It is checked on the "
        "workflow transition.")
    delivery_remark = fields.Text('Delivery Remarks')

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
        newpo = super(PurchaseOrder, self).copy(default=default)

        if initial_origin and 'requisition_id' in default:
            newpo.sudo().origin == initial_origin
        return newpo


class PurchaseOrderLineClassic(osv.orm.Model):
    _inherit = "purchase.order.line"

    def read_group(self, *args, **kwargs):
        """Do not aggregate price and qty. We need to do it this way as there
        is no group_operator that can be set to prevent aggregating float"""

        result = super(PurchaseOrderLineClassic, self).read_group(*args,
                                                                  **kwargs)

        for res in result:
            if 'price_unit' in res:
                del res['price_unit']
            if 'product_qty' in res:
                del res['product_qty']
            if 'lead_time' in res:
                del res['lead_time']
        return result


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    remark = fields.Text('Remarks / Conditions')
    requisition_line_id = fields.Many2one(
        'purchase.requisition.line',
        'Call for Bid Line',
        readonly=True)
