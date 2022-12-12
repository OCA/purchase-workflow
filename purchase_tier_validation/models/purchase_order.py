# Copyright 2017 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class PurchaseOrder(models.Model):
    _name = "purchase.order"
    _inherit = ["purchase.order", "tier.validation"]
    _state_from = ["draft", "sent", "to approve"]
    _state_to = ["purchase", "approved"]

    _tier_validation_manual_config = False

    # Do not merge purchase orders under validation
    def _make_po_get_domain(self, company_id, values, partner):
        domain = super()._make_po_get_domain(company_id, values, partner)
        domain += (('reviewer_ids', '=', False), )
        return domain
