# Copyright 2025 Open Source Integrators
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def action_view_approved_suppliers(self):
        """Action to view approved suppliers for this product variant"""
        self.ensure_one()
        return self.product_tmpl_id.action_view_approved_suppliers()

    def is_supplier_approved(self, partner_id, date=None):
        """Check if a supplier is approved for this product on a specific date"""
        self.ensure_one()
        return self.product_tmpl_id.is_supplier_approved(partner_id, date)
