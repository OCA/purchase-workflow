# Copyright 2020 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PurchaseOrder(models.Model):

    _inherit = "purchase.order"

    purchase_warn_msg = fields.Text(compute="_compute_purchase_warn_msg")

    @api.depends(
        "state",
        "partner_id.purchase_warn",
        "partner_id.commercial_partner_id.purchase_warn",
    )
    def _compute_purchase_warn_msg(self):
        for rec in self:
            purchase_warn_msg = ""
            if rec.partner_id:
                if rec.state in ["done", "cancel"]:
                    rec.purchase_warn_msg = ""
                    continue
                p = rec.partner_id.commercial_partner_id
                separator = ""
                if p.purchase_warn == "warning":
                    separator = "\n"
                    purchase_warn_msg += p.purchase_warn_msg
                if p != rec.partner_id and rec.partner_id.purchase_warn == "warning":
                    purchase_warn_msg += separator + rec.partner_id.purchase_warn_msg
            rec.purchase_warn_msg = purchase_warn_msg or False
