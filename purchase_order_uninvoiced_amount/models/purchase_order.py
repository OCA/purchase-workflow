# Copyright 2020 Tecnativa - Manuel Calero
# Copyright 2020 Tecnativa - Pedro M. Baeza
# Copyright 2020 Tecnativa - João Marques
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.depends("order_line.qty_invoiced")
    def _compute_amount_uninvoiced(self):
        for order in self:
            amount_uninvoiced = order.amount_untaxed
            for line in order.order_line.filtered("qty_invoiced"):
                # we use this way for being compatible with purchase_discount
                price_unit = (
                    line.product_qty
                    and line.price_subtotal / line.product_qty
                    or line.price_unit
                )
                amount_uninvoiced -= line.qty_invoiced * price_unit
            order.update(
                {"amount_uninvoiced": order.currency_id.round(amount_uninvoiced)}
            )

    amount_uninvoiced = fields.Monetary(
        string="Uninvoiced Amount",
        readonly=True,
        compute="_compute_amount_uninvoiced",
        tracking=True,
    )
