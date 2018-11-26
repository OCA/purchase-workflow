# Copyright 2018 Tecnativa - Vicent Cubells <vicent.cubells@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3

from odoo import api, fields, models
from .res_company import SORTING_CRITERIA, SORTING_DIRECTION


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    line_order = fields.Selection(
        selection=SORTING_CRITERIA,
        string='Sort Lines By',
        default=lambda self: self.env.user.company_id.default_po_line_order,
    )
    line_direction = fields.Selection(
        selection=SORTING_DIRECTION,
        string='Sort Direction',
        default=lambda self:
            self.env.user.company_id.default_po_line_direction,
    )

    @api.onchange('line_order')
    def onchange_line_order(self):
        if not self.line_order:
            self.line_direction = False

    @api.multi
    def _sort_purchase_line(self):
        if not self.line_order and not self.line_direction:
            return
        order = self.line_order
        reverse = self.line_direction == 'desc'
        sequence = 0
        key = eval("lambda p: p.%s" % order)
        for line in self.order_line.sorted(key=key, reverse=reverse):
            sequence += 10
            line.sequence = sequence

    @api.multi
    def write(self, values):
        res = super(PurchaseOrder, self).write(values)
        if 'order_line' in values or 'line_order' in values or \
                'line_direction' in values:
            self._sort_purchase_line()
        return res

    @api.model
    def create(self, values):
        purchase = super(PurchaseOrder, self).create(values)
        purchase._sort_purchase_line()
        return purchase
