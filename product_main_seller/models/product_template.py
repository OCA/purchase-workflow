# Copyright (C) 2022 - Today: GRAP (http://www.grap.coop)
# @author: Quentin DUPONT (quentin.dupont@grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

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
        for template in self:
            if template.variant_seller_ids:
                template.main_seller_id = fields.first(
                    template.variant_seller_ids.filtered(
                        lambda seller: seller.partner_id.active
                        and (
                            not seller.date_start
                            or seller.date_start <= fields.Date.today()
                        )
                        and (
                            not seller.date_end
                            or seller.date_end >= fields.Date.today()
                        )
                    )
                ).partner_id
            else:
                template.main_seller_id = False
