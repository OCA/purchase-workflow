# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class PurchaseApprovalBlockReason(models.Model):
    _name = 'purchase.approval.block.reason'

    name = fields.Char(required=True)
    description = fields.Text()
    active = fields.Boolean(default=True)
