# -*- coding: utf-8 -*-
# Copyright 2016 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from openerp import _, api, exceptions, fields, models


class PurchaseRequestLine(models.Model):
    _inherit = "purchase.request.line"

    @api.multi
    @api.depends('purchase_lines')
    def _compute_is_editable(self):
        super(PurchaseRequestLine, self)._compute_is_editable()
        for rec in self.filtered(lambda p: p in self and p.requisition_lines):
            rec.is_editable = False

    @api.multi
    def _compute_requisition_qty(self):
        for rec in self:
            requisition_qty = 0.0
            for requisition_line in rec.requisition_lines:
                if requisition_line.requisition_id.state != 'cancel':
                    requisition_qty += requisition_line.product_qty
            rec.requisition_qty = requisition_qty

    @api.multi
    @api.depends('requisition_lines.requisition_id.state')
    def _compute_requisition_state(self):
        for rec in self:
            temp_req_state = False
            if rec.requisition_lines:
                if any([pr_line.requisition_id.state == 'done' for
                        pr_line in
                        rec.requisition_lines]):
                    temp_req_state = 'done'
                elif all([pr_line.requisition_id.state == 'cancel'
                          for pr_line in rec.requisition_lines]):
                    temp_req_state = 'cancel'
                elif any([pr_line.requisition_id.state == 'in_progress'
                          for pr_line in rec.requisition_lines]):
                    temp_req_state = 'in_progress'
                elif all([pr_line.requisition_id.state in ('draft', 'cancel')
                          for pr_line in rec.requisition_lines]):
                    temp_req_state = 'draft'
            rec.requisition_state = temp_req_state

    requisition_lines = fields.Many2many(
        'purchase.requisition.line',
        'purchase_request_purchase_requisition_line_rel',
        'purchase_request_line_id',
        'purchase_requisition_line_id',
        string='Purchase Requisition Lines', readonly=True, copy=False)

    requisition_qty = fields.Float(compute='_compute_requisition_qty',
                                   string='Quantity in a Bid')
    requisition_state = fields.Selection(
        compute='_compute_requisition_state', string="Bid Status",
        type='selection', selection=lambda self: self.env[
            'purchase.requisition']._columns['state'].selection,
        store=True)

    is_editable = fields.Boolean(compute='_compute_is_editable',
                                 string="Is editable")

    @api.multi
    def unlink(self):
        for line in self:
            if line.requisition_lines:
                raise exceptions.Warning(
                    _('You cannot delete a record that refers to purchase '
                      'lines!'))
        return super(PurchaseRequestLine, self).unlink()
