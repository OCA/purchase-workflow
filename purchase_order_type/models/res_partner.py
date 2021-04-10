# Copyright 2015 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    purchase_type = fields.Many2one(
        comodel_name="purchase.order.type", string="Purchase Order Type"
    )
