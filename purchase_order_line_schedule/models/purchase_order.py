# Copyright 2021 ForgeFlow, S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import fields, models


class PurchaseOrderLine(models.Model):

    _inherit = "purchase.order.line"

    schedule_line_ids = fields.Many2one(
        comodel_name="purchase.order.line.schedule",
        inverse_name="order_line_id",
        string="Schedule Lines",
    )
