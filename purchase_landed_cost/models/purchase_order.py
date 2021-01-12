# Copyright 2013 Joaquín Gutierrez
# Copyright 2014-2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3

from odoo import models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def action_open_landed_cost(self):
        self.ensure_one()
        line_obj = self.env["purchase.cost.distribution.line"]
        lines = line_obj.search([("purchase_id", "=", self.id)])
        if lines:
            return lines.get_action_purchase_cost_distribution()
