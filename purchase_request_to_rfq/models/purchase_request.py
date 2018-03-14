# -*- coding: utf-8 -*-
# Copyright 2016 Eficent Business and IT Consulting Services S.L.
# Copyright 2016 Acsone SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import _, api, exceptions, fields, models


class PurchaseRequestLine(models.Model):

    _inherit = "purchase.request.line"

    @api.multi
    @api.depends('purchase_lines')
    def _compute_is_editable(self):
        super(PurchaseRequestLine, self)._compute_is_editable()
        for rec in self.filtered(lambda p: p.purchase_lines):
            rec.is_editable = False

    @api.multi
    def _compute_purchased_qty(self):
        for rec in self:
            rec.purchased_qty = 0.0
            for line in rec.purchase_lines.filtered(
                    lambda x: x.state != 'cancel'):
                if rec.product_uom_id and\
                        line.product_uom != rec.product_uom_id:
                    rec.purchased_qty += line.product_uom._compute_quantity(
                        line.product_qty, rec.product_uom_id)
                else:
                    rec.purchased_qty += line.product_qty

    @api.multi
    @api.depends('purchase_lines.state', 'purchase_lines.order_id.state')
    def _compute_purchase_state(self):
        for rec in self:
            temp_purchase_state = False
            if rec.purchase_lines:
                if any([po_line.state == 'done' for po_line in
                        rec.purchase_lines]):
                    temp_purchase_state = 'done'
                elif all([po_line.state == 'cancel' for po_line in
                          rec.purchase_lines]):
                    temp_purchase_state = 'cancel'
                elif any([po_line.state == 'purchase' for po_line in
                          rec.purchase_lines]):
                    temp_purchase_state = 'purchase'
                elif any([po_line.state == 'to approve' for po_line in
                          rec.purchase_lines]):
                    temp_purchase_state = 'to approve'
                elif any([po_line.state == 'sent' for po_line in
                          rec.purchase_lines]):
                    temp_purchase_state = 'sent'
                elif all([po_line.state in ('draft', 'cancel') for po_line in
                          rec.purchase_lines]):
                    temp_purchase_state = 'draft'
            rec.purchase_state = temp_purchase_state

    purchased_qty = fields.Float(string='Quantity in RFQ or PO',
                                 compute="_compute_purchased_qty")
    purchase_lines = fields.Many2many(
        'purchase.order.line', 'purchase_request_purchase_order_line_rel',
        'purchase_request_line_id',
        'purchase_order_line_id', 'Purchase Order Lines',
        readonly=True, copy=False)
    purchase_state = fields.Selection(
        compute="_compute_purchase_state",
        string="Purchase Status",
        selection=lambda self:
        self.env['purchase.order']._fields['state'].selection,
        store=True,
    )

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
    def _get_supplier_min_qty(self, product, partner_id=False):
        seller_min_qty = 0.0
        if partner_id:
            seller = product.seller_ids \
                .filtered(lambda r: r.name == partner_id) \
                .sorted(key=lambda r: r.min_qty)
        else:
            seller = product.seller_ids.sorted(key=lambda r: r.min_qty)
        if seller:
            seller_min_qty = seller[0].min_qty
        return seller_min_qty

    @api.model
    def _calc_new_qty(self, request_line, po_line=None, cancel=False,
                      new_pr_line=False):
        purchase_uom = po_line.product_uom or request_line.product_id.uom_po_id
        uom = request_line.product_uom_id
        qty = uom._compute_quantity(request_line.product_qty, purchase_uom)
        # Make sure we use the minimum quantity of the partner corresponding
        # to the PO. This does not apply in case of dropshipping
        supplierinfo_min_qty = 0.0
        if not po_line.order_id.dest_address_id:
            supplierinfo_min_qty = self._get_supplier_min_qty(
                po_line.product_id, po_line.order_id.partner_id)

        rl_qty = 0.0
        # Recompute quantity by adding existing running procurements.
        for rl in po_line.purchase_request_lines:
            rl_qty += rl.product_uom_id._compute_quantity(
                rl.product_qty, purchase_uom)
        new_qty = 0.0
        if not new_pr_line:
            new_qty = qty + po_line.product_qty

        qty = max(rl_qty, supplierinfo_min_qty, new_qty)

        return qty

    @api.multi
    def unlink(self):
        if self.mapped('purchase_lines'):
            raise exceptions.Warning(
                _('You cannot delete a record that refers to purchase '
                  'lines!'))
        return super(PurchaseRequestLine, self).unlink()
