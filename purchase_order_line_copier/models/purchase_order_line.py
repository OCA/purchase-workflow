# Copyright 2026 Heliconia Solutions Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import Command, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def action_open_copy_lines_wizard(self):
        self.ensure_one()
        ctx = self.env.context or {}
        line_ids = []

        if ctx.get("active_model") == "purchase.order.line":
            line_ids = ctx.get("active_ids", [])
        elif ctx.get("active_line_ids"):
            line_ids = ctx.get("active_line_ids", [])
        elif ctx.get("active_ids"):
            line_ids = ctx.get("active_ids", [])

        return {
            "name": "Copy Purchase Lines",
            "type": "ir.actions.act_window",
            "res_model": "copy.purchase.line.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_order_id": self.id,
                "default_line_ids": [Command.set(line_ids)] if line_ids else False,
            },
        }


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def action_open_copy_lines_wizard(self):
        ctx = self.env.context or {}
        if self:
            order = self.mapped("order_id")[:1]
            line_ids = self.ids
        else:
            order = None
            order_id = ctx.get("default_order_id")
            if not order_id and ctx.get("active_model") == "purchase.order":
                order_id = ctx.get("active_id")
            if order_id:
                order = self.env["purchase.order"].browse(order_id)
                line_ids = order.order_line.ids
            else:
                line_ids = []
        return {
            "name": "Copy Purchase Lines",
            "type": "ir.actions.act_window",
            "res_model": "copy.purchase.line.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_order_id": order.id if order else False,
                "active_ids": line_ids,
                "active_model": "purchase.order.line",
            },
        }

    def purchase_order_line_copy(self):
        self.copy(default={"order_id": self.order_id.id})
