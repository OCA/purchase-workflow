# Copyright 2021 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def write(self, vals):
        no_updated = self.filtered(lambda x: x.state not in ["purchase", "done"])
        res = super().write(vals)
        if vals.get("state", "") in ["purchase", "done"]:
            no_updated.mapped("order_line").update_supplierinfo_price()
        return res
