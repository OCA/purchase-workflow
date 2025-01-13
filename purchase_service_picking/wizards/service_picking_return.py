# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_is_zero


class ServiceReturnPicking(models.TransientModel):
    _name = "service.return.picking"
    _description = "Service Return Picking"

    @api.model
    def default_get(self, fields):
        if len(self.env.context.get("active_ids", list())) > 1:
            raise UserError(_("You may only return one picking at a time."))
        res = super().default_get(fields)
        if (
            self.env.context.get("active_id")
            and self.env.context.get("active_model") == "service.picking"
        ):
            picking = self.env["service.picking"].browse(
                self.env.context.get("active_id")
            )
            if picking.exists():
                res.update({"picking_id": picking.id})
        return res

    picking_id = fields.Many2one(comodel_name="service.picking")
    product_return_lines = fields.One2many(
        comodel_name="service.return.picking.line",
        inverse_name="wizard_id",
        string="Lines",
    )

    @api.onchange("picking_id")
    def _onchange_picking_id(self):
        product_return_lines = [(5,)]
        if self.picking_id and self.picking_id.state != "done":
            raise UserError(_("You may only return Done pickings."))
        spl_model = self.env["service.return.picking.line"]
        line_fields = [f for f in spl_model._fields.keys()]
        product_return_lines_data_tmpl = spl_model.default_get(line_fields)
        precision_digits = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        for line in self.picking_id.line_ids:
            if float_is_zero(line.product_uom_qty, precision_digits=precision_digits):
                continue
            product_return_lines_data = dict(product_return_lines_data_tmpl)
            product_return_lines_data.update(
                self._prepare_service_return_picking_line_vals(line)
            )
            product_return_lines.append((0, 0, product_return_lines_data))
        if self.picking_id and not product_return_lines:
            raise UserError(
                _(
                    "No products to return (only lines in Done state and not fully "
                    "returned yet can be returned)."
                )
            )
        if self.picking_id:
            self.product_return_lines = product_return_lines

    @api.model
    def _prepare_service_return_picking_line_vals(self, line):
        return {
            "product_id": line.product_id.id,
            "quantity": line.product_uom_qty,
            "line_id": line.id,
            "uom_id": line.product_id.uom_id.id,
        }

    def _create_return(self):
        precision_digits = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        if not self.product_return_lines:
            raise UserError(_("Please specify at least one service."))
        for line in self.product_return_lines:
            if float_is_zero(line.quantity, precision_digits=precision_digits):
                raise UserError(_("Please specify at least one non-zero quantity."))
            elif (
                float_compare(
                    line.quantity,
                    line.line_id.quantity_done,
                    precision_digits=precision_digits,
                )
                > 0
            ):
                raise UserError(
                    _("You cannot set a quantity greater than the quantity done.")
                )
        picking_line_vals = []
        new_picking = self.picking_id.copy(
            {
                "name": self.env["ir.sequence"].next_by_code("service.picking.return"),
                "state": "in_progress",
                "origin": _("Return of %s", self.picking_id.name),
            }
        )
        new_picking.message_post_with_view(
            "mail.message_origin_link",
            values={"self": new_picking, "origin": self.picking_id},
            subtype_id=self.env.ref("mail.mt_note").id,
        )
        for line in self.product_return_lines:
            if float_is_zero(line.quantity, precision_digits=precision_digits):
                continue
            picking_line_vals.append(line._prepare_picking_line_vals(new_picking))
        self.env["service.picking.line"].create(picking_line_vals)
        return new_picking

    def create_returns(self):
        new_picking = self._create_return()
        return {
            "name": _("Returned Picking"),
            "view_mode": "form,tree",
            "res_model": "service.picking",
            "res_id": new_picking.id,
            "type": "ir.actions.act_window",
            "context": dict(self.env.context),
        }


class ServiceReturnPickingLine(models.TransientModel):
    _name = "service.return.picking.line"
    _rec_name = "product_id"
    _description = "Service Return Picking Line"

    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product",
        required=True,
        domain="[('id', '=', product_id)]",
    )
    quantity = fields.Float(
        string="Quantity", digits="Product Unit of Measure", required=True
    )
    uom_id = fields.Many2one(
        comodel_name="uom.uom",
        string="Unit of Measure",
        related="line_id.product_uom_id",
    )
    wizard_id = fields.Many2one(comodel_name="service.return.picking", string="Wizard")
    line_id = fields.Many2one(
        comodel_name="service.picking.line",
        string="Line",
        required=True,
    )

    def _prepare_picking_line_vals(self, new_picking):
        return {
            "product_id": self.product_id.id,
            "product_uom_qty": self.quantity,
            "product_uom_id": self.uom_id.id,
            "picking_id": new_picking.id,
            "date": fields.Datetime.now(),
            "origin_returned_line_id": self.line_id.id,
            "purchase_line_id": self.line_id.purchase_line_id.id,
            "name": self.line_id.name,
        }
