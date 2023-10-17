# Copyright 2023 Camptocamp (<https://www.camptocamp.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models
from odoo.tools.safe_eval import safe_eval


class PurchaseTransportModeConstraints(models.Model):
    _name = "purchase.transport.mode.constraint"
    _description = "Transport Mode Constraint"

    name = fields.Char(required=True)
    description = fields.Char()
    purchase_domain = fields.Char(
        string="Source Purchase Domain",
        default=[],
        copy=False,
        help="Domain based on purchase",
    )

    purchase_transport_mode_id = fields.Many2one("purchase.transport.mode")

    def filter_valid_purchase(self, purchase):
        if not self.purchase_domain:
            return purchase
        domain = safe_eval(self.purchase_domain or "[]")
        if not domain:
            return purchase
        return purchase.filtered_domain(domain)
