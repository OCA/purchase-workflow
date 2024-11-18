# Copyright 2024 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    purchase_conditions = fields.Text(string="Terms and Conditions")

    def _commercial_fields(self):
        res = super()._commercial_fields()
        if self.env.company.is_partner_purchase_conditions_commercial:
            res += [
                "purchase_conditions",
            ]
        return res
