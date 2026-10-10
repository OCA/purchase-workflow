# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.tools import float_compare


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _is_price_unit_sync_restated(self, layer):
        """Whether the price difference of this invoice line has to be applied
        by restating the layer instead of by correcting only what is left of it.

        It needs `product_cost_price_avco_sync`, which is what replays the chain
        once the layer changes: restating it on its own, without that replay,
        would leave the layer inconsistent and would also throw away the
        correction Odoo does make, which is worse than not doing anything.

        Refunds are left to Odoo, they have a compensation logic of their own,
        and so is automated valuation, where the journal entry of the layer is
        already posted and restating it would pull the two apart.
        """
        self.ensure_one()
        if not hasattr(self.env["stock.valuation.layer"], "_cost_price_avco_sync"):
            return False
        product = self.product_id.with_company(self.company_id)
        return (
            not self.is_refund
            and product.cost_method == "average"
            and product.valuation != "real_time"
            and layer.stock_move_id
            and not layer.stock_valuation_layer_id
        )

    def _prepare_pdiff_vals(
        self, layer, aml, layer_price_unit, out_qty_to_invoice, qty_to_correct
    ):
        """Apply the invoiced price to the whole layer, not only to what is
        still on hand.

        Odoo corrects a price difference with a child layer worth the
        difference times the quantity that has not left stock yet, and sends the
        rest to the expense account. The stock ends up valued right, but the
        moves that already left keep the cost that turned out to be wrong, so
        the margin of what was sold, and any valuation asked for a date before
        the invoice, stay wrong too.

        Writing the invoiced price on the layer instead makes
        `product_cost_price_avco_sync` replay the chain, which corrects both,
        and leaves the bill on the same footing as changing the price on the
        purchase order, which this module already syncs. Odoo has done the hard
        part by the time this runs: which layer this invoice line pays for, and
        at what price, comes from its own matching of layers and bills.
        """
        if not self._is_price_unit_sync_restated(layer):
            return super()._prepare_pdiff_vals(
                layer, aml, layer_price_unit, out_qty_to_invoice, qty_to_correct
            )
        # Same conversion Odoo does to compare the invoiced price with the layer
        price_unit = aml._get_gross_unit_price() / aml.currency_rate
        price_unit = aml.product_uom_id._compute_price(
            price_unit, self.product_id.uom_id
        )
        precision = max(
            aml.currency_id.decimal_places,
            layer.currency_id.decimal_places,
            self.env["decimal.precision"].precision_get("Product Price"),
        )
        if float_compare(price_unit, layer_price_unit, precision_digits=precision):
            layer.unit_cost = price_unit
        # Nothing is left for Odoo to create: the correction is already in the
        # layer, and adding its child layer on top would count it twice.
        return [], []
