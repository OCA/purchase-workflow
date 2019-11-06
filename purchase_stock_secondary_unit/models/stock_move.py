# Copyright 2018-2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).
from odoo import api, fields, models
from odoo.tools.float_utils import float_round


class StockMove(models.Model):
    _inherit = ['stock.move', 'stock.secondary.unit.mixin']
    _name = 'stock.move'

    def _get_secondary_uom_qty(self):
        secondary_uom_qty = 0.0
        if self.product_uom and self.product_uom_qty and self.secondary_uom_id:
            factor = self.secondary_uom_id.factor * self.product_uom.factor
            secondary_uom_qty = float_round(
                self.product_uom_qty / (factor or 1.0),
                precision_rounding=self.secondary_uom_id.uom_id.rounding
            )
        return secondary_uom_qty

    secondary_uom_qty = fields.Float(default=_get_secondary_uom_qty)

    @api.onchange('product_uom_qty', 'secondary_uom_id', 'product_uom')
    def _onchange_uom_quantity(self):
        self.secondary_uom_qty = self._get_secondary_uom_qty()

