# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 (https://www.gnu.org/licenses/agpl-3.0.html)

from odoo import models
from odoo.exceptions import UserError


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def copy_pol(self):
        if self.filtered(
            lambda line: line.order_id.state == "cancel" or line.order_id.locked
        ):
            raise UserError(
                self.env._(
                    "You cannot copy lines from a canceled or locked purchase order."
                )
            )
        for line in self:
            line.copy(default={"order_id": line.order_id.id})
