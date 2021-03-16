# Copyright 2018 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import _, api, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.model
    def _purchase_request_picking_confirm_message_content(
        self, picking, request, request_dict
    ):
        if not request_dict:
            request_dict = {}
        title = _("Receipt confirmation %s for your Request %s") % (
            picking.name,
            request.name,
        )
        message = "<h3>%s</h3>" % title
        message += _(
            "The following requested items from Purchase Request %s "
            "have now been received in Incoming Shipment %s:"
        ) % (request.name, picking.name)
        message += "<ul>"
        for line in request_dict.values():
            message += _("<li><b>%s</b>: Received quantity %s %s</li>") % (
                line["name"],
                line["product_qty"],
                line["product_uom"],
            )
        message += "</ul>"
        return message

    def action_done(self):
        super(StockPicking, self).action_done()
        request_obj = self.env["purchase.request"]
        for picking in self:
            requests_dict = {}
            if picking.picking_type_id.code != "incoming":
                continue
            for move in picking.move_lines:
                if move.purchase_line_id:
                    for (
                        request_line
                    ) in move.purchase_line_id.sudo().purchase_request_lines:
                        request_id = request_line.request_id.id
                        if request_id not in requests_dict:
                            requests_dict[request_id] = {}
                        data = {
                            "name": request_line.name,
                            "product_qty": move.product_qty,
                            "product_uom": move.product_uom.name,
                        }
                        requests_dict[request_id][request_line.id] = data
            for request_id in requests_dict:
                request = request_obj.sudo().browse(request_id)
                message = self._purchase_request_picking_confirm_message_content(
                    picking, request, requests_dict[request_id]
                )
                if message is not None:  # override preparation method to avoid email
                    request.sudo().message_post(
                        body=message,
                        subtype="mail.mt_comment",
                        author_id=self.env.user.partner_id.id,
                    )
