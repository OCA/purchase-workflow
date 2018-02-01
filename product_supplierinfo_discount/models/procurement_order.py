# -*- coding: utf-8 -*-
# © 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, api


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.multi
    def _prepare_purchase_order_line(self, po, supplier):
        """
        Apply the discount to the created purchase order
        """
        res = super(ProcurementOrder, self)._prepare_purchase_order_line(
            po, supplier)
        seller = self.product_id._select_seller(
            partner_id=supplier.name,
            quantity=self.product_qty,
            date=po.date_order and po.date_order[:10],
            uom_id=self.product_uom)
        if seller:
            res['discount'] = seller.discount
        return res
