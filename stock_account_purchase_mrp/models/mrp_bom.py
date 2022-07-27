# Copyright 2022 Tecnativa - Pedro M. Baeza
# Copyright 2022 Tecnativa - César A. Sánchez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    valuation_price_type = fields.Selection(
        [
            ("none", "None"),
            ("by_lines", "Valuation by lines"),
            ("by_quantities", "Valuation by quantities"),
        ],
        default="none",
        help="Valuation by lines: Divide the cost of the product in all bom lines, and then"
        " divide this amount into the quantity of each bom line."
        "Valuation by quantities: Sum all quantities subcomponents and divide the the cost",
    )
    # add indexes for better performance on bom_find
    product_id = fields.Many2one(index=True)
    product_tmpl_id = fields.Many2one(index=True)
    company_id = fields.Many2one(index=True)
    type = fields.Selection(index=True)
