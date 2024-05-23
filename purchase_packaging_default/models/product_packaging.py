# Copyright 2024 Camptocamp (<https://www.camptocamp.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class ProductPackaging(models.Model):
    _inherit = "product.packaging"

    def _find_suitable_product_packaging(self, product_qty, uom_id):
        """Find nothing if you want to keep what was there."""
        if self.env.context.get("keep_product_packaging"):
            return self.browse()
        return super()._find_suitable_product_packaging(product_qty, uom_id)
