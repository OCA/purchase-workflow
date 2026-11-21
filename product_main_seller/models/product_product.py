# Copyright 2026 Tecnativa - Andrii Kompaniiets
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    main_seller_id = fields.Many2one(
        comodel_name="res.partner",
        string="Main Vendor",
        help="Put your supplier info in first position to set as main vendor",
        compute="_compute_main_seller_id",
        store=True,
    )

    @api.depends(
        "variant_seller_ids.sequence",
        "variant_seller_ids.partner_id.active",
        "variant_seller_ids.date_start",
        "variant_seller_ids.date_end",
    )
    def _compute_main_seller_id(self):
        for product in self:
            if product.variant_seller_ids:
                product.main_seller_id = fields.first(
                    product.variant_seller_ids.filtered(
                        lambda seller, p=product: seller.partner_id.active
                        and (
                            not seller.date_start
                            or seller.date_start <= fields.Date.today()
                        )
                        and (
                            not seller.date_end
                            or seller.date_end >= fields.Date.today()
                        )
                        and (not seller.product_id or seller.product_id == p)
                    )
                ).partner_id
            else:
                product.main_seller_id = False
