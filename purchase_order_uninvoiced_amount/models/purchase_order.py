# Copyright 2020 Tecnativa - Manuel Calero
# Copyright 2020 Tecnativa - Pedro M. Baeza
# Copyright 2020 Tecnativa - João Marques
# Copyright 2021 Tecnativa - Víctor Martínez
# Copyright 2026 Tecnativa - Anrii Kompaniiets
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.depends(
        "order_line.product_qty",
        "order_line.qty_invoiced",
        "order_line.qty_received",
        "order_line.product_id",
        "order_line.uom_id",
        "order_line.price_unit",
    )
    def _compute_amount_uninvoiced(self):
        for order in self:
            order.amount_uninvoiced = sum(
                order.order_line.mapped("price_subtotal_to_invoice")
            )

    amount_uninvoiced = fields.Monetary(
        string="Uninvoiced Amount",
        readonly=True,
        compute="_compute_amount_uninvoiced",
        tracking=True,
        store=True,
    )
