# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PurchaseOrderCancelReason(models.Model):
    _name = "purchase.order.cancel.reason"
    _description = "Purchase Order Cancel Reason"

    name = fields.Char(string="Reason", required=True, translate=True)
