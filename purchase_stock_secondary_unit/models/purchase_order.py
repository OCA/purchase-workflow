# Copyright 2018-2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).
from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.multi
    def _prepare_stock_moves(self, picking):
        """ If secondary unit of measure is defined on PO line propagate it
        to Stock Moves
        """
        res = super()._prepare_stock_moves(self, picking)
        if self.secondary_uom_id:
            res[0]['secondary_uom_id'] = self.secondary_uom_id
        return res
