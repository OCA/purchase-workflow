# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tools import float_compare
from odoo import api, models


class StockWarehouseOrderpoint(models.Model):

    _inherit = 'stock.warehouse.orderpoint'

    @api.multi
    def _quantity_in_progress(self):
        # In this method we need to access the purchase order line quantity
        # to correctly evaluate the forecast.
        # Imagine a product with a minimum rule of 4 units and a purchase
        # multiple of 12. The first run will generate a procurement for 4 Pc
        # but a purchase for 12 units.
        # Let's change the minimum rule to 5 units.
        # The standard subtract_procurements_from_orderpoints will return 4
        # and Odoo will create a procurement for 1 unit which will trigger a
        # purchase of 12 due to the multiple. So the original purchase will
        # be increased to 24 units which is wrong.
        # This override will return 12 and no additionnal procurement will be
        # created
        res = super()._quantity_in_progress()

        po_line_obj = self.env['purchase.order.line']

        purchase_lines = po_line_obj.search([
            ('orderpoint_id', 'in', self.ids),
            ('state', 'in',
             ['draft', 'sent', 'to approve'])
        ])
        purchase_lines.mapped('product_uom.rounding')
        purchase_lines.mapped('state')
        lines_by_orderpoint = dict.fromkeys(
            self.ids, po_line_obj)
        for line in purchase_lines:
            lines_by_orderpoint[line.orderpoint_id.id] |= line
        for orderpoint in self:
            lines = lines_by_orderpoint.get(orderpoint.id)
            if lines:
                po_lines = lines.filtered(
                    lambda x: x.state in ['draft', 'sent', 'to approve'])
                if po_lines:
                    qty = sum([line.product_qty for line in po_lines])
                    precision = orderpoint.product_uom.rounding
                    if float_compare(
                            qty, res[orderpoint.id],
                            precision_rounding=precision) >= 0:
                        res[orderpoint.id] = qty
        return res
