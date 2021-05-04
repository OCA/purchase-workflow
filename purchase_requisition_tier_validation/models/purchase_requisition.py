# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class PurchaseRequisition(models.Model):
    _name = "purchase.requisition"
    _inherit = ["purchase.requisition", "tier.validation"]
    _state_from = ["draft"]
    _state_to = ["ongoing", "in_progress"]

    _tier_validation_manual_config = False
