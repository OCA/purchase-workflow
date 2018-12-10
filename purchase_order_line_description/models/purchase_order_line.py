# Copyright 2015 Alex Comba - Agile Business Group
# Copyright 2017 Tecnativa - vicent.cubells@tecnativa.com
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.onchange('product_id')
    def onchange_product_id(self):
        res = super(PurchaseOrderLine, self).onchange_product_id()
        if not self.product_id:
            return res
        if (self.user_has_groups(
                'purchase_order_line_description.'
                'group_use_product_description_per_po_line') and
                self.product_id.description_purchase):
            self.name = self.product_id.description_purchase
        return res
