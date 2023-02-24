# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PurchaseRequisitionType(models.Model):
    _inherit = "purchase.requisition.type"

    quantity_copy = fields.Selection(
        selection_add=([("remaining_qty", "Use remaining quantities of agreement")]),
        ondelete={"remaining_qty": "set default"},
    )
