# Copyright 2017 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class PurchaseApprovalBlockReason(models.Model):
    _name = "purchase.approval.block.reason"
    _description = "Purchase Approval Block Reason"

    name = fields.Char(required=True)
    description = fields.Text()
    active = fields.Boolean(default=True)
