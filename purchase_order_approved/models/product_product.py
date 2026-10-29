# Copyright 2026 Versada UAB
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _get_lines_domain(self, location_ids=False, warehouse_ids=False):
        """Count approved orders like RFQs: they have no receipt yet."""
        domain = super()._get_lines_domain(location_ids, warehouse_ids)
        rfq_leaf = ("state", "in", ("draft", "sent", "to approve"))
        rfq_approved_leaf = ("state", "in", ("draft", "sent", "to approve", "approved"))
        return [rfq_approved_leaf if leaf == rfq_leaf else leaf for leaf in domain]
