# Copyright 2026 Jarsa
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    purchase_sales_history_years = fields.Integer(
        string="Sales History Years",
        config_parameter="purchase_line_sale_history.years_back",
        default=2,
        help="Number of past years, in addition to the current one, shown "
        "in the sales history of a purchase order line.",
    )
