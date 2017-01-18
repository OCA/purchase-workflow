# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    purchase_order_lines_count = fields.Float(
        compute='_compute_purchase_order_lines_count')

    @api.multi
    def _compute_purchase_order_lines_count(self):

        for partner in self.filtered(lambda x: x.supplier):
            domain = [('partner_id', 'child_of', partner.id)]
            partner.purchase_order_lines_count = self.env[
                'purchase.order.line'].search_count(domain)
