# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class PurchaseRequisitionLine(models.Model):
    _inherit = "purchase.requisition.line"

    name = fields.Text(compute="_compute_name", store=True, readonly=False)

    @api.depends("product_id")
    def _compute_name(self):
        """
        New method is triggered when the `product_id` field is changed.
        It updates the `name` field (description) with the product purchase
        description in the partner's language.
        """
        for line in self:
            if not line.product_id:
                continue
            partner = line.requisition_id.purchase_ids[:1].partner_id
            line.name = line.product_id.with_context(
                lang=partner.lang
            ).description_purchase
