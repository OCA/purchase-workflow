# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models


class PurchaseOrderMassCancel(models.TransientModel):
    _name = "purchase.order.mass.cancel"
    _description = "Wirzad Cancel PO"

    def confirm_cancel(self):
        orders = self.env["purchase.order"].browse(self.env.context.get("active_ids"))
        orders.button_cancel()
