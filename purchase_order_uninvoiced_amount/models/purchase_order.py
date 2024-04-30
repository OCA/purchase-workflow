# Copyright 2020 Tecnativa - Manuel Calero
# Copyright 2020 Tecnativa - Pedro M. Baeza
# Copyright 2020 Tecnativa - João Marques
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models
from odoo.tools.float_utils import float_compare


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.depends(
        "order_line.product_qty",
        "order_line.qty_invoiced",
        "order_line.qty_received",
        "order_line.product_id",
        "order_line.product_uom",
        "order_line.price_unit",
    )
    def _compute_amount_uninvoiced(self):
        for order in self:
            amount_uninvoiced = 0
            for line in order.order_line:
                # The qty to invoice depends on the invoicing policy of
                # the product
                if line.product_id.purchase_method == "purchase":
                    qty = line.product_qty - line.qty_invoiced
                else:
                    qty = line.qty_received - line.qty_invoiced
                rounding = line.product_uom.rounding
                if float_compare(qty, 0.0, precision_rounding=rounding) <= 0:
                    qty = 0.0
                # we use this way for being compatible with purchase_discount
                price_unit = (
                    line.product_qty
                    and line.price_subtotal / line.product_qty
                    or line.price_unit
                )
                amount_uninvoiced += qty * price_unit
            order.update(
                {"amount_uninvoiced": order.currency_id.round(amount_uninvoiced)}
            )

    amount_uninvoiced = fields.Monetary(
        string="Uninvoiced Amount",
        readonly=True,
        compute="_compute_amount_uninvoiced",
        tracking=True,
    )
