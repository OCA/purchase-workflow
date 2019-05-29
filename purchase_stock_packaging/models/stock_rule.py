# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockRule(models.Model):

    _inherit = 'stock.rule'

    @api.multi
    def _prepare_purchase_order_line(
            self, product_id, product_qty, product_uom, values, po, partner):
        """
        add packaging and update product_uom/quantity if necessary
        """

        self.ensure_one()
        res = super()._prepare_purchase_order_line(
            product_id, product_qty, product_uom, values, po, partner)
        supplier = values.get('supplier')
        if supplier.packaging_id:
            res['packaging_id'] = supplier.packaging_id.id
            new_uom_id = supplier.product_uom
            if new_uom_id.id != res['product_uom']:
                res['product_uom'] = new_uom_id
                qty = product_uom._compute_quantity(
                    product_qty, new_uom_id)
                res['product_qty'] = max(qty, supplier.min_qty)
        return res
