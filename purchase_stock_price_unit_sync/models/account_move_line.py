# Copyright 2025 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _generate_price_difference_vals(self, layers):
        # Remove svl_vals_list returned by the original module when
        # product_cost_price_avco_sync is installed because it will
        # make the synchronization.
        if self.env["ir.module.module"].search(
            [("name", "=", "product_cost_price_avco_sync"), ("state", "=", "installed")]
        ):
            return [[], []]
        return super()._generate_price_difference_vals(layers)
