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
        domain="[('id', 'in', wa_ids)]",
        copy=False,
    )
    wa_ids = fields.Many2many(
        comodel_name="work.acceptance",
        compute="_compute_wa_ids",
    )

    @api.depends("picking_type_id")
    def _compute_require_wa(self):
        for rec in self:
            if rec.picking_type_id.bypass_wa:
                rec.require_wa = False
            elif rec.picking_type_code == "incoming":
                rec.require_wa = self.env.user.has_group(
                    "purchase_work_acceptance.group_enforce_wa_on_in"
                )
            else:
                rec.require_wa = False

    @api.depends("require_wa")
    def _compute_wa_ids(self):
        for picking in self:
            picking.wa_ids = (
                self.env["work.acceptance"]
                .sudo()
                ._get_valid_wa("picking", picking.purchase_id.id)
            )

    def button_validate(self):
        for picking in self:
            if picking.wa_id:
                order_id = self._context.get("active_id")
                wa = (
                    self.env["work.acceptance"]
                    .sudo()
                    ._get_valid_wa("picking", order_id)
                )
                wa += picking.wa_id
                if picking.wa_id not in wa:
                    raise ValidationError(
                        _("%s was used in some picking.") % picking.wa_id.name
                    )
                wa_line = {}
                for line in picking.wa_id.wa_line_ids:
                    qty = line.product_uom._compute_quantity(
                        line.product_qty, line.product_id.uom_id
                    )
                    if qty > 0.0 and line.product_id.type in ["product", "consu"]:
                        wa_line[line.product_id.id] = (
                            wa_line.get(line.product_id.id, 0) + qty
                        )
                move_line = {}
                for move in picking.move_ids_without_package:
                    qty = move.product_uom._compute_quantity(
                        move.quantity_done, move.product_id.uom_id
                    )
                    if qty > 0.0:
                        move_line[move.product_id.id] = (
                            move_line.get(move.product_id.id, 0) + qty
                        )
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
                if line.product_id.id in wa_line:
                    wa_line[line.product_id.id] += qty
                else:
                    wa_line[line.product_id.id] = qty
            for move_line in self.move_line_ids_without_package:
                if move_line.product_id.id in wa_line:
                    qty = wa_line[move_line.product_id.id]
                    if move_line.product_uom_qty < qty:
                        move_line._origin.qty_done = move_line.product_uom_qty
                        wa_line[line.product_id.id] = qty - move_line.product_uom_qty
                    else:
                        move_line._origin.qty_done = qty


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    bypass_wa = fields.Boolean(
        string="WA not required",
        help="When 'Enforce WA on Goods Receipt' is set, this option type can by pass it",
    )
