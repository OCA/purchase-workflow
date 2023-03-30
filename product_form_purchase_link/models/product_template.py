# Copyright 2022 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    purchase_lines_count = fields.Float(
        compute="_compute_purchase_lines_count", string="Purchased products"
    )

    @api.depends("product_variant_ids.purchase_lines_count")
    def _compute_purchase_lines_count(self):
        for product in self:
            product.purchase_lines_count = sum(
                [
                    p.purchase_lines_count
                    for p in product.with_context(active_test=False).product_variant_ids
                ]
            )
