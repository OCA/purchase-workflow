# Copyright 2023 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    variant_specific_seller_ids = fields.One2many("product.supplierinfo", "product_id")

    supplier_partner_ids = fields.Many2many(
        comodel_name="res.partner",
        compute="_compute_supplier_partner_ids",
        search="_search_supplier_domain",
        string="Supplier Partner",
    )

    def _compute_supplier_partner_ids(self):
        for rec in self:
            rec.supplier_partner_ids = (
                rec.variant_specific_seller_ids.name.ids
                + rec.seller_ids.filtered(lambda s: not s.product_variant_ids).name.ids
            )

    def _search_supplier_domain(self, operator, value):
        return [
            "|",
            ("variant_specific_seller_ids.name.name", operator, value),
            "&",
            ("seller_ids.name.name", operator, value),
            ("product_variant_ids", "!=", False),
        ]
