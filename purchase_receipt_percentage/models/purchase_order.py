# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    receipt_percentage = fields.Float(
        compute="_compute_receipt_percentage",
        store=True,
        help="Receipt percentage between 0% and 100%",
    )
    receipt_percentage_display = fields.Float(
        compute="_compute_receipt_percentage",
        store=True,
        help="Technical field to be displayed in view. Its value is between"
        " 0 and 1, the percentage widget will format the value properly",
    )

    @api.depends("order_line.product_uom_qty", "order_line.receipt_percentage")
    def _compute_receipt_percentage(self):
        with_lines = self.filtered("order_line")
        (self - with_lines).update(
            {"receipt_percentage": 100, "receipt_percentage_display": 1}
        )
        for order in with_lines:
            num, den = 0, 0
            for line in order.order_line:
                qty = line.product_uom_qty or 1
                num += qty * line.receipt_percentage
                den += qty
            ratio = num / den
            order.update(
                {
                    "receipt_percentage": ratio,
                    # NB: we divide by 100 because we want this field to be in
                    # [0, 1], the percentage widget in the view will take care
                    # of displaying it correctly
                    "receipt_percentage_display": ratio / 100,
                }
            )
