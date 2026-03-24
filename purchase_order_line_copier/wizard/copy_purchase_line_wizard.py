# Copyright 2026 Heliconia Solutions Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import Command, api, fields, models
from odoo.exceptions import UserError


class CopyPurchaseLineWizard(models.TransientModel):
    _name = "copy.purchase.line.wizard"
    _description = "Wizard to Copy Multiple Purchase Lines"

    order_id = fields.Many2one("purchase.order", string="Purchase Order", readonly=True)
    line_ids = fields.One2many(
        "copy.purchase.line.wizard.line",
        "wizard_id",
        string="Lines to Copy",
    )
    select_all = fields.Boolean(
        compute="_compute_select_all",
        inverse="_inverse_select_all",
        store=False,
    )

    @api.depends("line_ids.selected")
    def _compute_select_all(self):
        for wizard in self:
            if wizard.line_ids:
                wizard.select_all = all(line.selected for line in wizard.line_ids)
            else:
                wizard.select_all = False

    def _inverse_select_all(self):
        for wizard in self:
            if wizard.line_ids:
                wizard.line_ids.write({"selected": wizard.select_all})

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        order_id = self.env.context.get("default_order_id")
        active_ids = self.env.context.get("active_ids", [])
        active_model = self.env.context.get("active_model")

        if order_id:
            order = self.env["purchase.order"].browse(order_id)
            selected_ids = (
                set(active_ids)
                if active_model == "purchase.order.line" and active_ids
                else set()
            )
            res["line_ids"] = [
                Command.create(
                    {
                        "line_id": line.id,
                        "selected": line.id in selected_ids if selected_ids else True,
                    }
                )
                for line in order.order_line
            ]
            res["order_id"] = order.id
        return res

    def action_copy_lines(self):
        self.ensure_one()
        lines = self.line_ids.filtered("selected").mapped("line_id")
        if self.order_id:
            lines = lines.filtered(lambda line: line.order_id.id == self.order_id.id)
        if not lines:
            raise UserError(self.env._("Please select at least one line to copy."))

        for line in lines:
            target_order = self.order_id or line.order_id
            line.copy(default={"order_id": target_order.id})

        return {"type": "ir.actions.client", "tag": "reload"}


class CopyPurchaseLineWizardLine(models.TransientModel):
    _name = "copy.purchase.line.wizard.line"
    _description = "Copy Purchase Line Wizard Line"

    wizard_id = fields.Many2one(
        "copy.purchase.line.wizard", required=True, ondelete="cascade"
    )
    line_id = fields.Many2one("purchase.order.line", required=True)
    selected = fields.Boolean(string="Copy")

    product_id = fields.Many2one(related="line_id.product_id", readonly=True)
    name = fields.Text(related="line_id.name", readonly=True)
    product_qty = fields.Float(related="line_id.product_qty", readonly=True)
    product_uom_id = fields.Many2one(related="line_id.product_uom_id", readonly=True)
    price_unit = fields.Float(related="line_id.price_unit", readonly=True)
    tax_ids = fields.Many2many(related="line_id.tax_ids", readonly=True)
    price_subtotal = fields.Monetary(related="line_id.price_subtotal", readonly=True)
    currency_id = fields.Many2one(related="line_id.currency_id", readonly=True)
    analytic_distribution = fields.Json(
        related="line_id.analytic_distribution", readonly=True
    )
    analytic_precision = fields.Integer(
        related="line_id.analytic_precision", readonly=True
    )

    def open_wizard(self):
        return {
            "name": "Copy Purchase Lines",
            "type": "ir.actions.act_window",
            "res_model": "copy.purchase.line.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_line_ids": self.env.context.get("active_ids")},
        }
