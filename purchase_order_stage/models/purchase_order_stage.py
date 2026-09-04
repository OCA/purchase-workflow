# Copyright 2022 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class PurchaseOrderStage(models.Model):
    _name = "purchase.order.stage"
    _description = "Stages of purchase orders"
    _order = "sequence"

    name = fields.Char(
        string="Description",
        translate=True,
        required=True,
    )
    active = fields.Boolean(
        default=True,
    )
    sequence = fields.Integer()
    fold = fields.Boolean()
