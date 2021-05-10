# Copyright 2019 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo import _, api, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.model
    def _purchase_order_picking_confirm_message_content(self, picking, purchase_dict):
        if not purchase_dict:
            purchase_dict = {}
        title = _("Receipt confirmation %s") % (picking.name)
        message = "<h3>%s</h3>" % title
        message += _(
            "The following items have now been received in Incoming Shipment %s:"
        ) % (picking.name)
        message += "<ul>"
        for purchase_line_id in purchase_dict.values():
            message += _("<li><b>%s</b>: Received quantity %s %s</li>") % (
                purchase_line_id["purchase_line"].product_id.display_name,
                purchase_line_id["stock_move"].product_qty,
                purchase_line_id["stock_move"].product_uom.name,
            )
        message += "</ul>"
        return message

    def _action_done(self):
        super()._action_done()
        for picking in self.filtered(lambda p: p.picking_type_id.code == "incoming"):
            purchase_dict = {}
            for move in picking.move_lines.filtered("purchase_line_id"):
                pol_id = move.purchase_line_id
                if pol_id.order_id not in purchase_dict.keys():
                    purchase_dict[pol_id.order_id] = {}
                if pol_id.id not in purchase_dict[pol_id.order_id].keys():
                    purchase_dict[pol_id.order_id][pol_id.id] = {}
                data = {"purchase_line": pol_id, "stock_move": move}
                purchase_dict[pol_id.order_id][pol_id.id] = data
            for po in purchase_dict.keys():
                message = self._purchase_order_picking_confirm_message_content(
                    picking, purchase_dict[po]
                )
                po.sudo().message_post(
                    body=message,
                    subtype_id=self.env.ref(
                        "purchase_reception_notify.mt_purchase_reception"
                    ).id,
                    author_id=self.env.user.partner_id.id,
                )
