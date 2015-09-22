# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Eficent (<http://www.eficent.com/>)
#              <contact@eficent.com>
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
from openerp import api, fields, models, _, exceptions
from datetime import datetime
from dateutil.relativedelta import relativedelta

_PURCHASE_ORDER_LINE_STATE = [
    ('none', 'No Purchase'),
    ('draft', 'RFQ'),
    ('confirmed', 'Confirmed'),
    ('done', 'Done'),
    ('cancel', 'Cancelled')
]


class PurchaseRequestLine(models.Model):

    _inherit = "purchase.request.line"

    @api.one
    @api.depends('purchase_lines')
    def _get_is_editable(self):
        super(PurchaseRequestLine, self)._get_is_editable()
        if self.purchase_lines:
            self.is_editable = False

    @api.one
    def _purchased_qty(self):
        purchased_qty = 0.0
        for purchase_line in self.purchase_lines:
            if purchase_line.state != 'cancel':
                purchased_qty += purchase_line.product_qty
        self.purchased_qty = purchased_qty

    @api.one
    @api.depends('purchase_lines.state')
    def _get_purchase_state(self):
        self.purchase_state = 'none'
        if self.purchase_lines:
            if any([po_line.state == 'done' for po_line in
                    self.purchase_lines]):
                self.purchase_state = 'done'
            elif all([po_line.state == 'cancel' for po_line in
                      self.purchase_lines]):
                self.purchase_state = 'cancel'
            elif any([po_line.state == 'confirmed' for po_line in
                      self.purchase_lines]):
                self.purchase_state = 'confirmed'
            elif all([po_line.state in ('draft', 'cancel') for po_line in
                      self.purchase_lines]):
                self.purchase_state = 'draft'

    purchased_qty = fields.Float(string='Quantity in RFQ or PO',
                                 compute="_purchased_qty")
    purchase_lines = fields.Many2many(
        'purchase.order.line', 'purchase_request_purchase_order_line_rel',
        'purchase_request_line_id',
        'purchase_order_line_id', 'Purchase Order Lines', readonly=True)
    purchase_state = fields.Selection(compute="_get_purchase_state",
                                      string="Purchase Status",
                                      selection=_PURCHASE_ORDER_LINE_STATE,
                                      store=True,
                                      default='none')

    @api.one
    def copy(self, default=None):
        if default is None:
            default = {}
        default.update({
            'purchase_lines': [],
        })
        return super(PurchaseRequestLine, self).copy(default)

    @api.model
    def _planned_date(self, request_line, delay=0.0):
        company = request_line.company_id
        date_planned = datetime.strptime(
            request_line.date_required, '%Y-%m-%d') - \
            relativedelta(days=company.po_lead)
        if delay:
            date_planned -= relativedelta(days=delay)
        return date_planned and date_planned.strftime('%Y-%m-%d') \
            or False

    @api.model
    def _calc_new_qty_price(self, request_line, po_line=None, cancel=False,
                            context=None):
        uom_obj = self.env['product.uom']
        qty = uom_obj._compute_qty(request_line.product_uom_id.id,
                                   request_line.product_qty,
                                   request_line.product_id.uom_po_id.id)
        # Make sure we use the minimum quantity of the partner corresponding
        # to the PO. This does not apply in case of dropshipping
        supplierinfo_min_qty = 0.0
        if po_line.order_id.location_id.usage != 'customer':
            if po_line.product_id.seller_id.id == \
                    po_line.order_id.partner_id.id:
                supplierinfo_min_qty = po_line.product_id.seller_qty
            else:
                supplierinfo_obj = self.env['product.supplierinfo']
                supplierinfos = supplierinfo_obj.search(
                    [('name', '=', po_line.order_id.partner_id.id),
                     ('product_id', '=', po_line.product_id.id)])
                if supplierinfos:
                    supplierinfo_min_qty = supplierinfos[0].min_qty

        if supplierinfo_min_qty == 0.0:
            qty += po_line.product_qty
        else:
            # Recompute quantity by adding existing running procurements.
            for rl in po_line.purchase_request_lines:
                qty += uom_obj._compute_qty(rl.product_uom_id.id,
                                            rl.product_qty,
                                            rl.product_id.uom_po_id.id)
            qty = max(qty, supplierinfo_min_qty) if qty > 0.0 else 0.0

        price = po_line.price_unit
        if qty != po_line.product_qty:
            pricelist_obj = self.env['product.pricelist']
            pricelist_id = po_line.order_id.partner_id.\
                property_product_pricelist_purchase.id
            price = pricelist_obj.price_get(
                [pricelist_id], request_line.product_id.id, qty,
                po_line.order_id.partner_id.id,
                {'uom': request_line.product_id.uom_po_id.id})[pricelist_id]

        return qty, price

    @api.multi
    def unlink(self):
        for line in self:
            if line.purchase_lines:
                raise exceptions.Warning(
                    _('You cannot delete a record that refers to purchase '
                      'lines!'))
        return super(PurchaseRequestLine, self).unlink()
