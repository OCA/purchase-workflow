# Copyright 2024 Akretion (https://www.akretion.com).
# @author Mathieu Delva <mathieu.delva@akretion.com>

from odoo import models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _update_move_date_deadline(self, new_date):
        res = super()._update_move_date_deadline(new_date)
        moves_to_update = self.move_ids.filtered(
            lambda m: m.state not in ("done", "cancel")
        )
        if not moves_to_update:
            moves_to_update = self.move_dest_ids.filtered(
                lambda m: m.state not in ("done", "cancel")
            )
        moves_to_update.date = new_date
        return res
