# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_price_unit(self):
        """Get correct price with discount replacing current price_unit
        value before calling super and restoring it later for assuring
        maximum inheritability.

        HACK: This is needed while https://github.com/odoo/odoo/pull/29983
        is not merged.
        """
        price_unit = False
        po_line = self.purchase_line_id
        if po_line and self.product_id == po_line.product_id:
            price = po_line._get_discounted_price_unit()
            if price != po_line.price_unit:
                # Only change value if it's different
                price_unit = po_line.price_unit
                po_line.price_unit = price
        res = super()._get_price_unit()
        if price_unit:
            po_line.price_unit = price_unit
        return res
