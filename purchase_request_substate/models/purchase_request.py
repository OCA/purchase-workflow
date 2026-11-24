# Copyright 2021 Ecosoft (<http://ecosoft.co.th>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class BaseSubstateType(models.Model):
    _inherit = "base.substate.type"

    model = fields.Selection(
        selection_add=[("purchase.request", "Purchase request")],
        ondelete={"purchase.request": "cascade"},
    )


class PurchaseRequest(models.Model):
    _inherit = ["purchase.request", "base.substate.mixin"]
    _name = "purchase.request"
    _state_field = "state"
