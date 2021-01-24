# Copyright 2013 Joaquín Gutierrez
# Copyright 2014-2016 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3
from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def action_open_landed_cost(self):
        self.ensure_one()
        line_obj = self.env["purchase.cost.distribution.line"]
        lines = line_obj.search([("picking_id", "=", self.id)])
        if lines:
            return lines.get_action_purchase_cost_distribution()
