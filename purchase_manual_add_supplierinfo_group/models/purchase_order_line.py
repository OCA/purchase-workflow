# Copyright 2024 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def action_create_missing_supplierinfo(self):
        vals = super().action_create_missing_supplierinfo()
        vals["context"]["skip_group_specific"] = True
        return vals
