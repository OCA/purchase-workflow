# -*- coding: utf-8 -*-
# Copyright 2015-17 Eficent Business and IT Consulting Services, S.L.
#           (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    product_supplier_code = fields.Char(
        string='Product Supplier Code',
        compute='_compute_product_supplier_code'
    )

    @api.multi
    @api.depends('product_id.seller_ids.name', 'partner_id',
                 'product_id.seller_ids.product_code')
    def _compute_product_supplier_code(self):
        for line in self:
            supplier_info = line.product_id.seller_ids.filtered(
                lambda s: (s.product_id == line.product_id and
                           s.name == line.partner_id))
            if supplier_info:
                code = supplier_info[0].product_code or ''
                line.product_supplier_code = code
