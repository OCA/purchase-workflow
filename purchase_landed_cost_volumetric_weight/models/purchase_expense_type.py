# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class PurchaseExpenseType(models.Model):
    _inherit = "purchase.expense.type"

    calculation_method = fields.Selection(
        selection_add=[("volumetric_weight", "Volumetric weight")],
    )
