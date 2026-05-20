# Copyright 2020 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    purchase_warn_msg = fields.Text(compute="_compute_purchase_warn_msg")

    @api.depends(
        "state",
        "partner_id.purchase_warn_msg",
        "partner_id.commercial_partner_id.purchase_warn_msg",
    )
    def _compute_purchase_warn_msg(self):
        for rec in self:
            purchase_warn_msg = False
            if rec.partner_id and rec.state != "cancel":
                p = rec.partner_id.commercial_partner_id
                messages = []
                if p.purchase_warn_msg:
                    messages.append(p.purchase_warn_msg)
                if p != rec.partner_id and rec.partner_id.purchase_warn_msg:
                    messages.append(rec.partner_id.purchase_warn_msg)
                purchase_warn_msg = "\n".join(messages) or False
            rec.purchase_warn_msg = purchase_warn_msg
