# Copyright 2023 Moduon Team S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)


from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    user_id = fields.Many2one(
        compute="_compute_user_id",
        store=True,
    )

    @api.depends("partner_id.purchase_manager_id")
    def _compute_user_id(self):
        for record in self:
            if record.state not in ("purchase", "done"):
                record.user_id = record.partner_id.purchase_manager_id
