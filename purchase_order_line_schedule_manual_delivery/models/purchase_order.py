# Copyright 2021 ForgeFlow, S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import _, models


class PurchaseOrder(models.Model):

    _inherit = "purchase.order"

    def button_schedule(self):
        for order in self:
            context = dict(self.env.context)
            context.update(default_order_id=order.id)
            return {
                "name": _("Schedule Order"),
                "type": "ir.actions.act_window",
                "res_model": "schedule.purchase.order",
                "view_mode": "form",
                "target": "new",
                "context": context,
            }
