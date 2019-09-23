# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
# Copyright 2019 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)

from odoo import api, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.multi
    def button_approve(self, force=False):
        res = super().button_approve(force)
        for rec in self:
            rec.order_line.mapped('product_id').set_product_last_purchase(
                rec.id)
        return res

    @api.multi
    def button_cancel(self):
        res = super().button_cancel()
        for rec in self:
            rec.order_line.mapped('product_id').set_product_last_purchase()
        return res
