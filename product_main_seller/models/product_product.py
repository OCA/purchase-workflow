# Copyright (C) 2022 - Today: GRAP (http://www.grap.coop)
# @author: Quentin DUPONT (quentin.dupont@grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    product_main_seller_partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Main Product Seller Partner",
        help="Put your supplier info in first position to set as main supplier",
        compute="_compute_main_seller_partner_id",
        store=True,
    )

    @api.multi
    @api.depends("variant_seller_ids.sequence", "variant_seller_ids.name")
    def _compute_main_seller_partner_id(self):
        for prod in self:
            if len(prod.variant_seller_ids):
                prod.product_main_seller_partner_id = prod.variant_seller_ids[0].name
