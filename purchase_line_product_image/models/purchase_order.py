# -*- coding: utf-8 -*-
# © 2017
#   @Lucky Kurniawan <kurniawanluckyy@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    product_image = fields.Binary(
        "image", related='product_id.product_tmpl_id.image_medium',
        help="Small-sized image of the product. It is automatically "
             "resized as a 64x64px image, with aspect ratio preserved. "
             "Use this field anywhere a small image is required.")
