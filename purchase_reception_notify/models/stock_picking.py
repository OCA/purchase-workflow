# Copyright 2019 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo import _, api, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.model
    def _purchase_order_picking_confirm_message_content(self, picking, stock_move_dict):
        if not stock_move_dict:
            stock_move_dict = {}
        title = _("Receipt confirmation %s") % (picking.name)
        message = "<h3>%s</h3>" % title
        message += _(
            "The following items have now been received in Incoming Shipment %s:"
        ) % (picking.name)
        message += "<ul>"
        for stock_move_id in stock_move_dict.values():
            message += _("<li><b>%s</b>: Received quantity %s %s</li>") % (
                stock_move_id["purchase_line"].product_id.display_name,
                stock_move_id["stock_move"].quantity_done,
                stock_move_id["stock_move"].product_uom.name,
            )
        message += "</ul>"
        return message

    def action_done(self):
        super(StockPicking, self).action_done()
        for picking in self.filtered(lambda p: p.picking_type_id.code == "incoming"):
            purchase_dict = {}
            for move in picking.move_lines.filtered(
                lambda x: x.purchase_line_id and x.quantity_done
            ):
                pol_id = move.purchase_line_id
                if pol_id.order_id not in purchase_dict.keys():
                    purchase_dict[pol_id.order_id] = {}
                if pol_id.id not in purchase_dict[pol_id.order_id].keys():
                    purchase_dict[pol_id.order_id][move.id] = {}
                data = {"purchase_line": pol_id, "stock_move": move}
                purchase_dict[pol_id.order_id][move.id] = data
            for po in purchase_dict.keys():
                message = self._purchase_order_picking_confirm_message_content(
                    picking, purchase_dict[po]
                )
                po.sudo().message_post(
                    body=message,
                    subtype="purchase_reception_notify.mt_purchase_reception",
                    author_id=self.env.user.partner_id.id,
                )
