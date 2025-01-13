# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class ServiceImmediateTransfer(models.TransientModel):
    _name = "service.immediate.transfer"
    _description = "Immediate Transfer"

    picking_ids = fields.Many2many(
        comodel_name="service.picking", relation="service_picking_transfer_rel"
    )
    line_ids = fields.One2many(
        comodel_name="service.immediate.transfer.line",
        inverse_name="immediate_transfer_id",
        string="Lines",
    )

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        if "line_ids" in fields and res.get("picking_ids"):
            res["line_ids"] = [
                (0, 0, {"to_immediate": True, "picking_id": pick_id})
                for pick_id in res["picking_ids"][0][2]
            ]
        return res

    def process(self):
        pickings_to_do = self.env["service.picking"]
        pickings_not_to_do = self.env["service.picking"]
        for line in self.line_ids:
            if line.to_immediate:
                pickings_to_do |= line.picking_id
            else:
                pickings_not_to_do |= line.picking_id

        for line in pickings_to_do.line_ids:
            line.quantity_done = line.product_uom_qty

        pickings_to_validate = self.env.context.get("action_validate_picking_ids")
        if pickings_to_validate:
            pickings_to_validate = self.env["service.picking"].browse(
                pickings_to_validate
            )
            pickings_to_validate = pickings_to_validate - pickings_not_to_do
            return pickings_to_validate.with_context(
                skip_immediate=True
            ).action_validate()
        return True


class ServiceImmediateTransferLine(models.TransientModel):
    _name = "service.immediate.transfer.line"
    _description = "Immediate Transfer Line"

    immediate_transfer_id = fields.Many2one(
        comodel_name="service.immediate.transfer",
        string="Immediate Transfer",
        required=True,
    )
    picking_id = fields.Many2one(
        comodel_name="service.picking", string="Transfer", required=True
    )
    to_immediate = fields.Boolean(string="To Process")
