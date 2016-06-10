# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L.
# - Jordi Ballester Alomar
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models, _, exceptions

_PURCHASE_REQUISITION_STATE = [
    ('none', 'No Bid'),
    ('draft', 'Draft'),
    ('in_progress', 'Confirmed'),
    ('open', 'Bid Selection'),
    ('done', 'PO Created'),
    ('cancel', 'Cancelled')]


class PurchaseRequestLine(models.Model):
    _inherit = "purchase.request.line"

    @api.one
    @api.depends('requisition_lines')
    def _get_is_editable(self):
        super(PurchaseRequestLine, self)._get_is_editable()
        if self.requisition_lines:
            self.is_editable = False

    @api.one
    def _requisition_qty(self):
        requisition_qty = 0.0
        for requisition_line in self.requisition_lines:
            if requisition_line.requisition_id.state != 'cancel':
                requisition_qty += requisition_line.product_qty
        self.requisition_qty = requisition_qty

    @api.one
    @api.depends('requisition_lines.requisition_id.state')
    def _get_requisition_state(self):
        self.requisition_state = 'none'
        if self.requisition_lines:
            if any([pr_line.requisition_id.state == 'done' for
                    pr_line in
                    self.requisition_lines]):
                self.requisition_state = 'done'
            elif all([pr_line.requisition_id.state == 'cancel'
                      for pr_line in self.requisition_lines]):
                self.requisition_state = 'cancel'
            elif any([pr_line.requisition_id.state == 'in_progress'
                      for pr_line in self.requisition_lines]):
                self.requisition_state = 'in_progress'
            elif all([pr_line.requisition_id.state in ('draft', 'cancel')
                      for pr_line in self.requisition_lines]):
                self.requisition_state = 'draft'

    requisition_lines = fields.Many2many(
        'purchase.requisition.line',
        'purchase_request_purchase_requisition_line_rel',
        'purchase_request_line_id',
        'purchase_requisition_line_id',
        string='Purchase Requisition Lines', readonly=True)

    requisition_qty = fields.Float(compute='_requisition_qty',
                                   string='Quantity in a Bid')
    requisition_state = fields.Selection(
        compute='_get_requisition_state', string="Bid Status",
        type='selection', selection=_PURCHASE_REQUISITION_STATE, store=True,
        default='none')

    is_editable = fields.Boolean(compute='_get_is_editable',
                                 string="Is editable")

    @api.one
    def copy(self, default=None):
        if default is None:
            default = {}
        default.update({
            'requisition_lines': [],
        })
        return super(PurchaseRequestLine, self).copy(default)

    @api.multi
    def unlink(self):
        for line in self:
            if line.requisition_lines:
                raise exceptions.Warning(
                    _('You cannot delete a record that refers to purchase '
                      'lines!'))
        return super(PurchaseRequestLine, self).unlink()
