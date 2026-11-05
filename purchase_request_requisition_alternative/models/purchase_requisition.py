# Copyright 2026 PopSolutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class PurchaseRequisitionCreateAlternative(models.TransientModel):
    _inherit = "purchase.requisition.create.alternative"

    def action_create_alternative(self):
        """Carry the purchase request links over to the new alternative.

        The wizard creates the alternative order, so the link is written on
        the new record rather than on the origin. Going through the origin
        here covers that path as well.
        """
        res = super().action_create_alternative()
        alternative = self.env["purchase.order"].browse(res.get("res_id", []))
        if alternative.exists():
            self.origin_po_id._link_purchase_requests_to(alternative)
        return res
