# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.fields import first


class PurchaseRequisitionLine(models.Model):
    _inherit = "purchase.requisition.line"

    name = fields.Text(
        string="Product Description", compute="_compute_name", store=True
    )

    @api.depends("product_id")
    def _compute_name(self):
        """
        New method is triggered when the `product_id` field is changed.
        It updates the `name` field (description) based on the selected product
        and the partner's language and purchase description.
        """
        for line in self:
            partner = first(line.requisition_id.purchase_ids).partner_id
            product_lang = line.product_id.with_context(
                lang=partner.lang, partner_id=partner.id
            )
            name = product_lang.display_name
            if product_lang.description_purchase:
                name += f"\n{product_lang.description_purchase}"
            line.name = name
