from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    hide_price = fields.Boolean(
        compute="_compute_hide_price", readonly=True, store=False
    )
    amount_untaxed_hide = fields.Monetary(
        string="Untaxed.", compute="_compute_hidden_prices"
    )
    amount_total_hide = fields.Monetary(
        string="Total.", compute="_compute_hidden_prices"
    )

    @api.depends("partner_id.commercial_partner_id.hide_purchase_price")
    @api.depends_context("uid")
    def _compute_hide_price(self):
        for rec in self:
            rec.hide_price = (
                bool(rec.partner_id) and rec.partner_id._hide_purchase_price()
            )

    @api.depends("amount_total", "amount_untaxed", "hide_price")
    def _compute_hidden_prices(self):
        for rec in self:
            if rec.hide_price:
                rec.amount_total_hide = 0.0
                rec.amount_untaxed_hide = 0.0
            else:
                rec.amount_total_hide = rec.amount_total
                rec.amount_untaxed_hide = rec.amount_untaxed
