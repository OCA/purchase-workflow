# Copyright 2019 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ProcurementRule(models.Model):
    _inherit = 'procurement.rule'

    def _prepare_purchase_order_line(self, product_id, product_qty,
                                     product_uom, values, po, supplier):
        """Apply the discount to the created purchase order"""
        res = super(ProcurementRule, self)._prepare_purchase_order_line(
            product_id, product_qty, product_uom, values, po, supplier)
        date = None
        if po.date_order:
            date = fields.Date.to_string(
                fields.Date.from_string(po.date_order))
        seller = product_id._select_seller(
            partner_id=supplier.name,
            quantity=product_qty,
            date=date, uom_id=product_uom)
        if seller:
            res['discount2'] = seller.discount2
            res['discount3'] = seller.discount3
        return res
