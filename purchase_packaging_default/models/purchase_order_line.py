# Copyright 2024 Camptocamp (<https://www.camptocamp.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import math

from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _get_default_packaging(self):
        """From product get 1st packaging found ordered by sequence"""
        product_template = self.product_id.product_tmpl_id
        return fields.first(product_template.packaging_ids)

    @api.onchange("product_id")
    def _onchange_product_id(self):
        if self.env.user.company_id.purchase_packaging_default_enabled:
            product_packaging = self._get_default_packaging()
            if product_packaging:
                self.product_packaging_id = product_packaging

    @api.depends("product_id", "product_qty", "product_uom")
    def _compute_product_packaging_id(self):
        _self = self
        if self.env.user.company_id.purchase_packaging_default_enabled:
            _self = _self.with_context(keep_product_packaging=True)
        return super(PurchaseOrderLine, _self)._compute_product_packaging_id()

    @api.depends("product_packaging_id", "product_uom", "product_qty")
    def _compute_product_packaging_qty(self):
        res = super()._compute_product_packaging_qty()
        for line in self:
            if line.product_packaging_qty:
                packaging_uom = line.product_packaging_id.product_uom_id
                packaging_uom_qty = line.product_uom._compute_quantity(
                    line.product_qty, packaging_uom
                )
                # Super computes product_packaging_qty rounding it to packaging_uom.precision.
                # We must round up that value as we won't sell 0.5, 1.6 boxes/pallets
                line.product_packaging_qty = math.ceil(
                    packaging_uom_qty / line.product_packaging_id.qty
                )
        return res
