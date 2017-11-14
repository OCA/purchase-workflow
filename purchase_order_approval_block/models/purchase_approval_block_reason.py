# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class PurchaseApprovalBlockReason(models.Model):
    _name = 'purchase.approval.block.reason'

    name = fields.Char(required=True)
    description = fields.Text()
    active = fields.Boolean(default=True)
