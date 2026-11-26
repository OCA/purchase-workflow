from odoo import api, fields, models


class ProductSupplierinfo(models.Model):
    _inherit = "product.supplierinfo"

    hide_price = fields.Boolean(compute="_compute_hide_price")

    @api.depends("partner_id.commercial_partner_id.hide_purchase_price")
    @api.depends_context("uid")
    def _compute_hide_price(self):
        for rec in self:
            rec.hide_price = (
                bool(rec.partner_id) and rec.partner_id._hide_purchase_price()
            )
