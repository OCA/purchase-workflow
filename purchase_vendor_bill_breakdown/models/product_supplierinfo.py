from odoo import api, fields, models


class ProductSupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    price = fields.Float(
        compute="_compute_price",
        inverse="_inverse_price",
        store=True,
    )
    price_manual = fields.Float(
        string="Price",
        digits="Product Price",
        copy=False,
    )

    @api.onchange("price")
    def _inverse_price(self):
        """Set custom price when price field changed"""
        for record in self.filtered(
            lambda rec: not (rec.component_ids and rec.partner_use_components)
        ):
            record.price_manual = record.price

    @api.depends(
        "component_ids",
        "component_ids.price_total",
        "price_manual",
        "partner_use_components",
    )
    def _compute_price(self):
        """Compute price by components price"""
        for rec in self:
            if rec.component_ids and rec.partner_use_components:
                rec.price = sum(rec.component_ids.mapped("price_total"))
            elif rec.price_manual:
                rec.price = rec.price_manual
