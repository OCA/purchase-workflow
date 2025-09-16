# Copyright 2025 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    receipt_status = fields.Selection(compute="_compute_oca_receipt_status")
