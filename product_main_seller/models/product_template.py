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

    @api.depends("variant_seller_ids.sequence", "variant_seller_ids.partner_id")
    def _compute_main_seller_id(self):
        for template in self:
            if template.variant_seller_ids:
                template.main_seller_id = template.variant_seller_ids[0].partner_id
            else:
                template.main_seller_id = False
