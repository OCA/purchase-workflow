# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
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
            rec.require_wa = False
            if (
                not rec.picking_type_id.bypass_wa
                and rec.picking_type_code == "incoming"
            ):
                rec.require_wa = self.env.user.has_group(
                    "purchase_work_acceptance.group_enforce_wa_on_in"
                )

    @api.depends("require_wa")
    def _compute_wa_ids(self):
        for picking in self:
            picking.wa_ids = (
                self.env["work.acceptance"]
                .sudo()
                ._get_valid_wa("picking", picking.purchase_id.id)
            )

    def button_validate(self):
        order_id = self.env.context.get("active_id")
        wa_obj = self.env["work.acceptance"].sudo()

        for picking in self:
            if not picking.wa_id:
                continue

            valid_was = wa_obj._get_valid_wa("picking", order_id)
            if picking.wa_id not in (valid_was | picking.wa_id):
                raise ValidationError(
                    self.env._(f"{picking.wa_id.name} was used in some picking.")
                )

            wa_line = {}
            for line in picking.wa_id.wa_line_ids:
                qty = line.product_uom._compute_quantity(
                    line.product_qty, line.product_id.uom_id
                )
                if qty > 0.0 and line.product_id.type == "consu":
                    wa_line[line.product_id.id] = (
                        wa_line.get(line.product_id.id, 0) + qty
                    )
            move_line = {}
            for move in picking.move_ids_without_package:
                qty = move.product_uom._compute_quantity(
                    move.quantity, move.product_id.uom_id
                )
                if qty > 0.0:
                    move_line[move.product_id.id] = (
                        move_line.get(move.product_id.id, 0) + qty
                    )
            if wa_line != move_line:
                raise ValidationError(
                    self.env._(
                        "You cannot validate a transfer if done quantity "
                        "not equal accepted quantity"
                    )
                )
        return super().button_validate()

    @api.onchange("wa_id")
    def _onchange_wa_id(self):
        """Change qty in picking more efficiently for large lines"""
        if not self.wa_id:
            return

        # Pre-compute all quantities in a single pass
        wa_line = {}
        for line in self.wa_id.wa_line_ids:
            product_id = line.product_id.id
            qty = line.product_uom._compute_quantity(
                line.product_qty, line.product_id.uom_id
            )
            wa_line[product_id] = wa_line.get(product_id, 0) + qty

        # Batch update move lines
        for move_line in self.move_line_ids_without_package:
            product_id = move_line.product_id.id
            if product_id in wa_line:
                qty = wa_line[product_id]
                if move_line.quantity < qty:
                    move_line._origin.quantity = move_line.quantity
                    wa_line[product_id] = qty - move_line.quantity
                else:
                    move_line._origin.quantity = qty


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    bypass_wa = fields.Boolean(
        string="WA not required",
        help="When 'Enforce WA on Goods Receipt' is set, "
        "this option type can by pass it",
    )
