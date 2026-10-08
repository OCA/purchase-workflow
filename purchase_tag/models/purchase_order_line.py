# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    tag_ids = fields.Many2many(
        comodel_name="purchase.tag",
        relation="purchase_order_line_tag_rel",
        column1="purchase_order_line_id",
        column2="tag_id",
        string="Tags",
    )
