# Copyright 2019 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    purchase_general_discount = fields.Float(
        digits="Discount",
        string="Purchase General Discount (%)",
        company_dependent=True,
    )
