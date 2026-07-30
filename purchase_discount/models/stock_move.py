# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from contextlib import contextmanager, suppress

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    @contextmanager
    def _ensure_product_price_precision(self, po_line, discounted_price):
        """
        Check if price_unit has enough decimals to store the precise discounted price.

        If not, use more decimals and restore the old ones after yield.
        """
        price_unit_precision = price_unit_precision_digits = False
        if po_line.price_unit != discounted_price:
            # We have to update the `decimal.precision` record
            # because it is directly used in `super._get_price_unit`
            price_unit_precision = (
                self.env["decimal.precision"]
                .sudo()
                .search([("name", "=", "Product Price")])
            )
            price_unit_precision_digits = price_unit_precision.digits
            price_unit_precision.digits += 8

        yield

        if price_unit_precision and price_unit_precision_digits:
            price_unit_precision.digits = price_unit_precision_digits

    def _get_price_unit(self):
        """Get correct price with discount replacing current price_unit
        value before calling super and restoring it later for assuring
        maximum inheritability.

        HACK: This is needed while https://github.com/odoo/odoo/pull/29983
        is not merged.
        """
        price_unit = False
        po_line = self.purchase_line_id.sudo()
        price = po_line._get_discounted_price_unit()
        if po_line and self.product_id == po_line.product_id:
            precision_context = self._ensure_product_price_precision(po_line, price)
        else:
            precision_context = suppress()

        with precision_context:
            if hasattr(self.env, "ocb"):
                res = super()._get_price_unit()
            else:
                if po_line and self.product_id == po_line.product_id:
                    if price != po_line.price_unit:
                        # Only change value if it's different
                        price_unit = po_line.price_unit
                        po_line.price_unit = price

                res = super()._get_price_unit()

        if price_unit:
            po_line.price_unit = price_unit
        return res
