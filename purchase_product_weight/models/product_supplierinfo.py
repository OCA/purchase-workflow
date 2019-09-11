# -*- coding: utf-8 -*-

from odoo import models, fields


class ProductSupplierinfo(models.Model):
    _inherit = 'product.supplierinfo'

    compute_price_on_weight = fields.Boolean(
        related='product_tmpl_id.compute_price_on_weight')
