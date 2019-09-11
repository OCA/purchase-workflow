# -*- coding: utf-8 -*-

from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    compute_price_on_weight = fields.Boolean(
        help='Price is computed on weight of product and not on default u.m.')
