# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class Picking(models.Model):
    _inherit = "stock.picking"

    require_wa = fields.Boolean(compute="_compute_require_wa")
    wa_id = fields.Many2one(
        comodel_name="work.acceptance",
        string="WA Reference",
        copy=False,
    )

    def _compute_require_wa(self):
        if self.picking_type_code == "incoming":
            self.require_wa = self.env.user.has_group(
                "purchase_work_acceptance.group_enforce_wa_on_in"
            )
        else:
            self.require_wa = False

    def button_validate(self):
        if self.wa_id:
            order = self.env["purchase.order"].browse(self._context.get("active_id"))
            if any(
                picking.wa_id == self.wa_id and picking != self
                for picking in order.picking_ids
            ):
                raise ValidationError(
                    _("%s was used in some picking.") % self.wa_id.name
                )
            wa_line = {}
            for line in self.wa_id.wa_line_ids:
                qty = line.product_uom._compute_quantity(
                    line.product_qty, line.product_id.uom_id
                )
                if qty > 0.0 and line.product_id.type in ["product", "consu"]:
                    if line.product_id.id in wa_line.keys():
                        qty_old = wa_line[line.product_id.id]
                        wa_line[line.product_id.id] = qty_old + qty
                    else:
                        wa_line[line.product_id.id] = qty
            move_line = {}
            for move in self.move_ids_without_package:
                qty = move.product_uom._compute_quantity(
                    move.quantity_done, line.product_id.uom_id
                )
                if qty > 0.0:
                    if move.product_id.id in move_line.keys():
                        qty_old = move_line[move.product_id.id]
                        move_line[move.product_id.id] = qty_old + qty
                    else:
                        move_line[move.product_id.id] = qty
            if wa_line != move_line:
                raise ValidationError(
                    _(
                        "You cannot validate a transfer if done"
                        " quantity not equal accepted quantity"
                    )
                )
        return super(Picking, self).button_validate()

    @api.onchange("wa_id")
    def _onchange_wa_id(self):
        if self.wa_id:
            wa_line = {}
            for line in self.wa_id.wa_line_ids:
                qty = line.product_uom._compute_quantity(
                    line.product_qty, line.product_id.uom_id
                )
                if line.product_id.id in wa_line.keys():
                    qty_old = wa_line[line.product_id.id]
                    wa_line[line.product_id.id] = qty_old + qty
                else:
                    wa_line[line.product_id.id] = qty
            for move_line in self.move_line_ids_without_package:
                if move_line.product_id.id in wa_line.keys():
                    qty = wa_line[move_line.product_id.id]
                    if move_line.product_uom_qty < qty:
                        move_line._origin.qty_done = move_line.product_uom_qty
                        wa_line[line.product_id.id] = qty - move_line.product_uom_qty
                    else:
                        move_line._origin.qty_done = qty
