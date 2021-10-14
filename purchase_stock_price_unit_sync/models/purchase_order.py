# Copyright 2019 Carlos Dauden - Tecnativa <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def write(self, vals):
        res = super().write(vals)
        if ('price_unit' in vals or 'discount' in vals) and (
                not self.env.context.get('skip_stock_price_unit_sync')):
            self.stock_price_unit_sync()
        return res

    def stock_price_unit_sync(self):
        for line in self.filtered(lambda l: l.state in ['purchase', 'done']):
            # When the affected product is a kit we do nothing, which is the
            # default behavior on the standard: the move is exploded into moves
            # for the components and those get the default price_unit for the
            # time being. We avoid a hard dependency as well.
            if (
                hasattr(line.product_id, "bom_ids")
                and line.product_id._is_phantom_bom()
            ):
                continue
            line.move_ids.write({
                'price_unit': line.with_context(skip_stock_price_unit_sync=True
                                                )._get_stock_move_price_unit(),
            })
