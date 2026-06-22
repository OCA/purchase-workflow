# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools import float_compare


class ProductSupplierinfo(models.Model):
    _inherit = "product.supplierinfo"

    secondary_uom_id = fields.Many2one(
        comodel_name="product.secondary.unit",
        string="Secondary Unit",
        domain="[('product_tmpl_id', '=', product_tmpl_id)]",
    )
    secondary_uom_price = fields.Float(
        string="Secondary Price",
        digits="Product Price",
        compute="_compute_secondary_uom_price",
        inverse="_inverse_secondary_uom_price",
        store=True,
    )

    @api.depends("price", "secondary_uom_id", "secondary_uom_id.factor")
    def _compute_secondary_uom_price(self):
        for rec in self:
            if rec.secondary_uom_id:
                rec.secondary_uom_price = rec.price * rec.secondary_uom_id.factor
            else:
                rec.secondary_uom_price = 0.0

    @api.onchange("secondary_uom_price")
    def _inverse_secondary_uom_price(self):
        precision = self.env["decimal.precision"].precision_get("Product Price")
        for rec in self:
            if rec.secondary_uom_id:
                expected_secondary_price = rec.price * rec.secondary_uom_id.factor
                if (
                    rec.price
                    and float_compare(
                        rec.secondary_uom_price,
                        expected_secondary_price,
                        precision_digits=precision,
                    )
                    == 0
                ):
                    continue
                rec.price = rec.secondary_uom_price / rec.secondary_uom_id.factor

    @api.onchange("product_tmpl_id", "product_id")
    def _onchange_product_id_secondary_uom(self):
        self.secondary_uom_id = (
            self.product_id.purchase_secondary_uom_id
            or self.product_tmpl_id.purchase_secondary_uom_id
        )
