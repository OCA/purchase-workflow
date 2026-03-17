# Copyright 2026 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    def _get_filtered_supplier(self, company_id, product_id, params=False):
        """To avoid confusion with the _compute_domain() method in ir.rule linked to
        product.supplierinfo, we will filter the records in this method.
        If the user does not have "advanced permissions" (condition), we will
        retrieve the records using sudo() and then filter them by the partners we have
        obtained—that is, those to which the user has access
        """
        user = self.env.user
        group1 = "purchase_security.group_purchase_own_orders"
        group3 = "purchase.group_purchase_manager"
        condition = (
            not self.env.su and user.has_group(group1) and not user.has_group(group3)
        )
        _self = self.sudo() if condition else self
        sellers = super(SupplierInfo, _self)._get_filtered_supplier(
            company_id=company_id, product_id=product_id, params=params
        )
        if condition:
            partners = self.env["res.partner"].search(
                [("id", "in", sellers.partner_id.ids)]
            )
            sellers = sellers.filtered(lambda x: x.partner_id in partners)
        return sellers
