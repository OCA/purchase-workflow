from odoo import models
from odoo.osv import expression


class StockMove(models.Model):

    _inherit = "stock.move"

    def _search_picking_for_assignation_domain(self):
        domain = super()._search_picking_for_assignation_domain()
        if self.env.context.get("purchase_delivery_split_date"):
            domain = expression.AND(
                [domain, [("scheduled_date", "=", self.date_deadline)]]
            )
        return domain
