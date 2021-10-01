from odoo import models, _, fields, api
from odoo.exceptions import UserError


class InvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    landed_cost_id = fields.Many2one("stock.landed.cost", readonly=True)
    landed_cost_ok = fields.Boolean(related="product_id.landed_cost_ok", readonly=True)
    invoice_state = fields.Selection([
        ("draft", "Draft"),
        ("open", "Open"),
        ("in_payment", "In Payment"),
        ("paid", "Paid"),
        ("cancel", "Cancelled"),
    ], related="invoice_id.state", readonly=True)

    def _default_landed_cost_journal(self):
        return self.env["account.journal"].search([
            ("type", "=", "general"),
        ], limit=1)

    def create_landed_cost(self):
        self.ensure_one()
        if self.landed_cost_id:
            return self.invoice_id.action_view_landed_costs()
        if not self.product_id:
            raise UserError(_(
                "Can't create landed cost for invoice line without product"))
        if self.purchase_line_id:
            pickings = self.purchase_line_id.order_id.mapped("picking_ids")
        else:
            pickings = self.invoice_id.mapped(
                "invoice_line_ids.purchase_line_id.order_id.picking_ids")
        account_journal_id = self._default_landed_cost_journal()
        if not account_journal_id:
            raise UserError(_("Can't find a general journal"))
        lc = self.env["stock.landed.cost"].create({
            "date": self.invoice_id.date,
            "account_journal_id": account_journal_id.id,
            "picking_ids": [
                (6, 0, pickings.ids)],
            "cost_lines": [(0, 0, {
                "product_id": self.product_id.id,
                "name": self.name,
                "account_id": self.account_id.id,
                "split_method": self.product_id.split_method,
                "price_unit": self.price_subtotal,
            })],
        })
        lc.compute_landed_cost()
        self.landed_cost_id = lc.id

        return self.invoice_id.action_view_landed_costs()


class Invoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def action_view_landed_costs(self):
        lc_ids = self.mapped("invoice_line_ids.landed_cost_id")
        action = self.env.ref("stock_landed_costs.action_stock_landed_cost")
        result = action.read()[0]
        if not lc_ids or len(lc_ids) > 1:
            result["domain"] = "[('id','in',%s)]" % lc_ids.ids
        elif len(lc_ids) == 1:
            res = self.env.ref("stock_landed_costs.view_stock_landed_cost_form", False)
            form_view = [(res and res.id or False, "form")]
            if "views" in result:
                result["views"] = form_view + [
                    (state, view) for state, view in result["views"] if view != "form"]
            else:
                result["views"] = form_view
            result["res_id"] = lc_ids.id
        return result
