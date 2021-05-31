# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    wa_count = fields.Integer(compute="_compute_wa_ids", string="WA count", default=0)
    wa_ids = fields.One2many(
        comodel_name="work.acceptance",
        compute="_compute_wa_ids",
        string="Work Acceptances",
    )
    wa_line_ids = fields.One2many(
        comodel_name="work.acceptance.line",
        inverse_name="purchase_line_id",
        string="WA Lines",
        readonly=True,
    )
    wa_accepted = fields.Boolean(string="WA Accepted", compute="_compute_wa_accepted")

    def _compute_wa_ids(self):
        for order in self:
            order.wa_ids = (
                order.mapped("order_line").mapped("wa_line_ids").mapped("wa_id")
            )
            order.wa_count = len(order.wa_ids)

    def action_view_wa(self):
        self.ensure_one()
        act = self.env.ref("purchase_work_acceptance.action_work_acceptance")
        result = act.sudo().read()[0]
        create_wa = self.env.context.get("create_wa", False)
        result["context"] = {
            "default_purchase_id": self.id,
            "default_partner_id": self.partner_id.id,
            "default_company_id": self.company_id.id,
            "default_currency_id": self.currency_id.id,
            "default_date_due": self.date_planned,
            "default_wa_line_ids": [
                (
                    0,
                    0,
                    {
                        "purchase_line_id": line.id,
                        "name": line.name,
                        "product_uom": line.product_uom.id,
                        "product_id": line.product_id.id,
                        "price_unit": line.price_unit,
                        "product_qty": line._get_product_qty(),
                    },
                )
                for line in self.order_line
                if line._get_product_qty() != 0
            ],
        }
        if len(self.wa_ids) > 1 and not create_wa:
            result["domain"] = "[('id', 'in', " + str(self.wa_ids.ids) + ")]"
        else:
            res = self.env.ref(
                "purchase_work_acceptance.view_work_acceptance_form", False
            )
            result["views"] = [(res and res.id or False, "form")]
            if not create_wa:
                result["res_id"] = self.wa_ids.id or False
        return result

    def action_create_invoice(self):
        if self.env.context.get("create_bill", False) and self.env.user.has_group(
            "purchase_work_acceptance.group_enable_wa_on_invoice"
        ):
            wizard = self.env.ref(
                "purchase_work_acceptance.view_select_work_acceptance_wizard"
            )
            return {
                "name": _("Select Work Acceptance"),
                "type": "ir.actions.act_window",
                "view_mode": "form",
                "res_model": "select.work.acceptance.wizard",
                "views": [(wizard.id, "form")],
                "view_id": wizard.id,
                "target": "new",
            }
        return super().action_create_invoice()

    def _compute_wa_accepted(self):
        for order in self:
            lines = order.order_line.filtered(lambda l: l.qty_to_accept > 0)
            order.wa_accepted = not any(lines)


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    wa_line_ids = fields.One2many(
        comodel_name="work.acceptance.line",
        inverse_name="purchase_line_id",
        string="WA Lines",
        readonly=True,
    )
    qty_accepted = fields.Float(
        compute="_compute_qty_accepted",
        string="Accepted Qty.",
        store=True,
        readonly=True,
        digits="Product Unit of Measure",
    )
    qty_to_accept = fields.Float(
        compute="_compute_qty_accepted",
        string="To Accept Qty.",
        store=True,
        readonly=True,
        digits="Product Unit of Measure",
    )

    def _get_product_qty(self):
        return self.product_qty - sum(
            wa_line.product_qty
            for wa_line in self.wa_line_ids
            if wa_line.wa_id.state != "cancel"
        )

    def _prepare_account_move_line(self, move=False):
        res = super()._prepare_account_move_line(move)
        if move and move.wa_id:
            wa_line = self.wa_line_ids.filtered(lambda l: l.wa_id == move.wa_id)
            res["quantity"] = wa_line.product_qty
            res["product_uom_id"] = wa_line.product_uom
        return res

    @api.depends(
        "wa_line_ids.wa_id.state",
        "wa_line_ids.product_qty",
        "product_qty",
        "product_uom_qty",
        "order_id.state",
    )
    def _compute_qty_accepted(self):
        for line in self:
            # compute qty_accepted
            qty = 0.0
            for wa_line in line.wa_line_ids.filtered(
                lambda l: l.wa_id.state == "accept"
            ):
                qty += wa_line.product_uom._compute_quantity(
                    wa_line.product_qty, line.product_uom
                )
            line.qty_accepted = qty

            # compute qty_to_accept
            line.qty_to_accept = line.product_uom_qty - line.qty_accepted
