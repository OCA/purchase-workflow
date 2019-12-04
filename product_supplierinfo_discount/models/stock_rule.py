# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# Copyright 2019 Tecnativa - Carlos Dauden
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _prepare_purchase_order_line(self, product_id, product_qty,
                                     product_uom, values, po, partner):
        """
        Apply the discount to the created purchase order
        """
        res = super()._prepare_purchase_order_line(
            product_id, product_qty, product_uom, values, po, partner)
        seller = product_id._select_seller(
            partner_id=partner,
            quantity=product_qty,
            date=po.date_order or None,
            uom_id=product_uom)
        if seller:
            res['discount'] = seller.discount
        return res
