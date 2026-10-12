from odoo import fields, models


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

    def _compute_hide_price(self):
        for rec in self:
            cial_partner = rec.partner_id.commercial_partner_id
            if (
                cial_partner
                and cial_partner.hide_purchase_price
                and self.env.user.has_group(
                    "purchase_hide_price.purchase_hide_price_grp"
                )
            ):
                rec.hide_price = True
            else:
                rec.hide_price = False

    def _compute_hidden_prices(self):
        for rec in self:
            if rec.hide_price:
                rec.amount_total_hide = 0.0
                rec.amount_untaxed_hide = 0.0
            else:
                rec.amount_total_hide = rec.amount_total
                rec.amount_untaxed_hide = rec.amount_untaxed
