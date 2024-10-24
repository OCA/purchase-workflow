# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockRoute(models.Model):
    _inherit = "stock.route"

    force_vendor_with_best_promotion = fields.Boolean(default=False)
