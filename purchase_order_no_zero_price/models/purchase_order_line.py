# Copyright (C) 2022 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, exceptions, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.constrains("price_unit", "display_type", "state")
    def _check_price_unit_zero(self):
        # Prevent zero prices on confirmed POs
        # to help ensure proper Stock Valuation
        # when receiving the products
        # Also supports `purchase_triple_discount` module
        no_price_lines = self.filtered(
            lambda x: not x.display_type
            and x.state not in ["draft", "cancel"]
            and not x.price_unit
            # Allow zero price for 100% discounts:
            and getattr(x, "discount", 0.0) != 100.0
            and getattr(x, "discount2", 0.0) != 100.0
            and getattr(x, "discount3", 0.0) != 100.0
        )
        if no_price_lines:
            raise exceptions.UserError(
                _("Missing unit price for Products: %s")
                % ", ".join(no_price_lines.product_id.mapped("display_name"))
            )
