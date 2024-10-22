# Copyright 2022 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    # Only select Partners approved for Purchase
    partner_id = fields.Many2one(
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)"
        ", ('purchase_ok', '=', True)]",
    )
    dest_address_id = fields.Many2one(
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)"
        ", ('purchase_ok', '=', True)]",
    )

    @api.model
    def _get_under_validation_exceptions(self):
        # If Tier Validation is installed, allow writing in the Exceptions field
        # (method provided by base_tier_validation))
        exception_fields = super()._get_under_validation_exceptions()
        exception_fields.append("exception_ids")
        return exception_fields
