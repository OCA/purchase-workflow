# -*- coding: utf-8 -*-
# Copyright 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    # These field names are for avoiding conflicts with any other field with
    # the same name declared by other modules and that can be a no related one
    product_tmpl_id_purchase_order_variant_mgmt = fields.Many2one(
        comodel_name="product.template", related="product_id.product_tmpl_id",
        readonly=True
    )
    state_purchase_order_variant_mgmt = fields.Selection(
        related="order_id.state",
        readonly=True
    )
    product_attribute_value_ids = fields.Many2many(
        comodel_name='product.attribute.value',
        related="product_id.attribute_value_ids",
        readonly=True
    )
