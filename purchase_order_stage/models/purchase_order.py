# Copyright 2022 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    stage_id = fields.Many2one(
        string="Stage",
        comodel_name="purchase.order.stage",
    )
