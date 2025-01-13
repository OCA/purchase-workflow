# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, fields, models
from odoo.tools.float_utils import float_compare


class ServiceBackorderConfirmation(models.TransientModel):
    _name = "service.backorder.confirmation"
    _description = "Backorder Confirmation"

    picking_ids = fields.Many2many(
        comodel_name="service.picking", relation="service_picking_backorder_rel"
    )
    line_ids = fields.One2many(
        comodel_name="service.backorder.confirmation.line",
        inverse_name="backorder_confirmation_id",
        string="Lines",
    )

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        if "line_ids" in fields and res.get("picking_ids"):
            res["line_ids"] = [
                (0, 0, {"to_backorder": True, "picking_id": pick_id})
                for pick_id in res["picking_ids"][0][2]
            ]
        return res

    def _check_less_quantities_than_expected(self, pickings):
        for picking in pickings:
            moves_to_log = {}
            for line in picking.line_ids:
                if (
                    float_compare(
                        line.product_uom_qty,
                        line.quantity_done,
                        precision_rounding=line.product_uom_id.rounding,
                    )
                    > 0
                ):
                    moves_to_log[line] = (line.quantity_done, line.product_uom_qty)
            if moves_to_log:
                picking._log_less_quantities_than_expected(moves_to_log)

    def process(self):
        pickings_to_do = self.env["service.picking"]
        pickings_not_to_do = self.env["service.picking"]
        for line in self.line_ids:
            if line.to_backorder is True:
                pickings_to_do |= line.picking_id
            else:
                pickings_not_to_do |= line.picking_id

        pickings_to_validate = self.env.context.get("action_validate_picking_ids")
        if pickings_to_validate:
            pickings = (
                self.env["service.picking"]
                .browse(pickings_to_validate)
                .with_context(skip_backorder=True)
            )
            if pickings_not_to_do:
                pickings = pickings.with_context(
                    picking_ids_not_to_backorder=pickings_not_to_do.ids
                )
            return pickings.action_validate()
        return True

    def process_cancel_backorder(self):
        pickings_to_validate_ids = self.env.context.get("action_validate_picking_ids")
        if pickings_to_validate_ids:
            pickings = self.env["service.picking"].browse(pickings_to_validate_ids)
            return pickings.with_context(
                skip_backorder=True, picking_ids_not_to_backorder=self.picking_ids.ids
            ).action_validate()
        return True


class ServiceBackorderConfirmationLine(models.TransientModel):
    _name = "service.backorder.confirmation.line"
    _description = "Backorder Confirmation Line"

    backorder_confirmation_id = fields.Many2one(
        comodel_name="service.backorder.confirmation", string="Immediate Transfer"
    )
    picking_id = fields.Many2one(comodel_name="service.picking", string="Transfer")
    to_backorder = fields.Boolean(string="To Backorder")
