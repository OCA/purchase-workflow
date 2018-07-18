# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields, api


class PurchaseOrderLine(models.Model):

    _inherit = 'purchase.order.line'

    procurement_group_id = fields.Many2one('procurement.group')

    def _merge_in_existing_line(self, product_id, product_qty, product_uom,
                                location_id, name, origin, values):
        """Do no merge PO lines if procurement group is different."""
        if values.get('group_id') != self.procurement_group_id:
            return False
        return super()._merge_in_existing_line(
            product_id, product_qty, product_uom, location_id, name, origin,
            values)

    @api.multi
    def _prepare_stock_moves(self, picking):
        res = super()._prepare_stock_moves(picking)
        res[0]['group_id'] = (
            self.procurement_group_id.id or self.order_id.group_id.id)
        return res
