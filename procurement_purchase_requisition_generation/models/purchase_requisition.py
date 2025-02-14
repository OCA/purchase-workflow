# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PurchaseRequisition(models.Model):
    _inherit = "purchase.requisition"

    procurement_group_id = fields.Many2one(
        comodel_name="procurement.group", string="Procurement Group", copy=False
    )
