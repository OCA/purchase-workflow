# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PurchaseUpdateDateConfirmation(models.TransientModel):
    _name = "purchase.update.date.confirmation"
    _description = "Purchase Update Date Confirmation"

    purchase_order_id = fields.Many2one(
        comodel_name="purchase.order",
        ondelete="cascade",
        readonly=True,
    )
    current_date_planned = fields.Datetime(
        related="purchase_order_id.current_date_planned"
    )

    def doit(self):
        for wizard in self:
            return wizard.purchase_order_id.with_context(
                purchase_order_update_date=True
            ).button_confirm()
        return True
