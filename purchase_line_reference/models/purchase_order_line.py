# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    reference = fields.Reference(
        selection='_get_references',
        help='Link to the record that this purchase order line directly '
             'represents.',
    )

    @api.model
    def _get_references(self):
        all_models = self.env['ir.model'].search([])
        return [(m.model, m.name) for m in all_models]
