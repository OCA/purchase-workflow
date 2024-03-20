# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class PurchaseOrderLineStockMoveCancel(models.TransientModel):

    _name = "purchase.order.line.stock.move.cancel"
    _description = "Wizard to cancel stock move from purchase order line"

    purchase_line_ids = fields.Many2many(
        comodel_name="purchase.order.line",
        ondelete="cascade",
        required=True,
        readonly=True,
    )

    def process(self):
        for wizard in self:
            wizard.purchase_line_ids._cancel_moves()
        return True
