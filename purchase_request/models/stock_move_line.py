# Copyright 2017 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import _, api, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    @api.model
    def _purchase_request_confirm_done_message_content(self, message_data):
        title = _("Receipt confirmation %s for your Request %s") % (
            message_data["picking_name"],
            message_data["request_name"],
        )
        message = "<h3>%s</h3>" % title
        message += _(
            "The following requested items from Purchase Request %s "
            "have now been received in %s using Picking %s:"
        ) % (
            message_data["request_name"],
            message_data["location_name"],
            message_data["picking_name"],
        )
        message += "<ul>"
        message += _("<li><b>%s</b>: Transferred quantity %s %s</li>") % (
            message_data["product_name"],
            message_data["product_qty"],
            message_data["product_uom"],
        )
        message += "</ul>"
        return message

    @api.model
    def _picking_confirm_done_message_content(self, message_data):
        title = _("Receipt confirmation for Request %s") % (
            message_data["request_name"]
        )
        message = "<h3>%s</h3>" % title
        message += _(
            "The following requested items from Purchase Request %s "
            "requested by %s "
            "have now been received in %s:"
        ) % (
            message_data["request_name"],
            message_data["requestor"],
            message_data["location_name"],
        )
        message += "<ul>"
        message += _("<li><b>%s</b>: Transferred quantity %s %s</li>") % (
            message_data["product_name"],
            message_data["product_qty"],
            message_data["product_uom"],
        )
        message += "</ul>"
        return message

    def _prepare_message_data(self, ml, request, allocated_qty):
        return {
            "request_name": request.name,
            "picking_name": ml.picking_id.name,
            "product_name": ml.product_id.name_get()[0][1],
            "product_qty": allocated_qty,
            "product_uom": ml.product_uom_id.name,
            "location_name": ml.location_dest_id.name_get()[0][1],
            "requestor": request.requested_by.partner_id.name,
        }

    def allocate(self):
        for ml in self.filtered(
            lambda m: m.exists() and m.move_id.purchase_request_allocation_ids
        ):

            # We do sudo because potentially the user that completes the move
            #  may not have permissions for purchase.request.
            to_allocate_qty = ml.qty_done
            to_allocate_uom = ml.product_uom_id
            for allocation in ml.move_id.purchase_request_allocation_ids.sudo():
                allocated_qty = 0.0
                if allocation.open_product_qty and to_allocate_qty:
                    to_allocate_uom_qty = to_allocate_uom._compute_quantity(
                        to_allocate_qty, allocation.product_uom_id
                    )
                    allocated_qty = min(
                        allocation.open_product_qty, to_allocate_uom_qty
                    )
                    allocation.allocated_product_qty += allocated_qty
                    to_allocate_uom_qty -= allocated_qty
                    to_allocate_qty = allocation.product_uom_id._compute_quantity(
                        to_allocate_uom_qty, to_allocate_uom
                    )

                request = allocation.purchase_request_line_id.request_id
                if allocated_qty:
                    message_data = self._prepare_message_data(
                        ml, request, allocated_qty
                    )
                    message = self._purchase_request_confirm_done_message_content(
                        message_data
                    )
                    if (
                        message is not None
                    ):  # override preparation method to avoid email
                        request.message_post(body=message, subtype="mail.mt_comment")

                    picking_message = self._picking_confirm_done_message_content(
                        message_data
                    )
                    if (
                        picking_message is not None
                    ):  # override preparation method to avoid email
                        ml.move_id.picking_id.message_post(
                            body=picking_message, subtype="mail.mt_comment"
                        )

                allocation._compute_open_product_qty()

    def _action_done(self):
        res = super(StockMoveLine, self)._action_done()
        self.allocate()
        return res
