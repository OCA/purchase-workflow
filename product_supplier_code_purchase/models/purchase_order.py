# -*- coding: utf-8 -*-
# Copyright 2015-17 Eficent Business and IT Consulting Services, S.L.
#           (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.multi
    def _compute_product_supplier_code(self):
        product_supplierinfo_obj = self.env['product.supplierinfo']
        for line in self:
            partner = line.order_id.partner_id
            product = line.product_id
            if product and partner:
                supplier_info = product_supplierinfo_obj.search([
                    '|', ('product_tmpl_id', '=', product.product_tmpl_id.id),
                    ('product_id', '=', product.id),
                    ('name', '=', partner.id)], limit=1)
                if supplier_info:
                    code = supplier_info.product_code or ''
                    line.product_supplier_code = code
        return True

    product_supplier_code = fields.Char(string='Product Supplier Code',
                                        compute=_compute_product_supplier_code)
