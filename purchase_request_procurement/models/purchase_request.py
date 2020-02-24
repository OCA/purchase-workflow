# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PurchaseRequest(models.Model):

    _inherit = 'purchase.request'

    group_id = fields.Many2one(
        'procurement.group', string="Procurement Group", copy=False)

    @api.multi
    def _check_rejected_allowed(self):
        if any([s == 'done' for s in self.mapped(
                'line_ids.procurement_id.state')]):
            raise ValidationError(
                _('You cannot reject a purchase request with lines related '
                  'to done procurement orders.'))

    @api.multi
    def button_rejected(self):
        self._check_rejected_allowed()
        return super(PurchaseRequest, self).button_rejected()

    @api.multi
    def _check_reset_allowed(self):
        if any([s == 'done' for s in self.mapped(
                'line_ids.procurement_id.state')]):
            raise ValidationError(
                _('You cannot set back to draft a purchase request with '
                  'lines related to done procurement orders.'))

    @api.multi
    def button_draft(self):
        self._check_reset_allowed()
        return super(PurchaseRequest, self).button_draft()
