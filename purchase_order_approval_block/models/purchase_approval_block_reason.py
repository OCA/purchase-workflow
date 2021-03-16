# Copyright 2017 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class PurchaseApprovalBlockReason(models.Model):
    _name = "purchase.approval.block.reason"
    _description = "Purchase Approval Block Reason"

    name = fields.Char(required=True)
    description = fields.Text()
    active = fields.Boolean(default=True)
