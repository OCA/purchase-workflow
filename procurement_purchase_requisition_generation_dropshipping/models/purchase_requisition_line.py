# Copyright 2025 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PurchaseRequisitionLine(models.Model):
    _inherit = "purchase.requisition.line"

    sale_line_id = fields.Many2one("sale.order.line", string="Origin Sale Order Line")

    def _prepare_purchase_order_line(
        self, name, product_qty=0.0, price_unit=0.0, taxes_ids=False
    ):
        res = super()._prepare_purchase_order_line(
            name, product_qty, price_unit, taxes_ids
        )
        if self.sale_line_id:
            res["sale_line_id"] = self.sale_line_id.id
        return res
