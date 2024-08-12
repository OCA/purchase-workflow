# Copyright 2017-19 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import functools

from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    # adding discount2 and discount3 to depends
    @api.depends("discount2", "discount3")
    def _compute_amount(self):
        return super()._compute_amount()

    discount2 = fields.Float(
        "Disc. 2 (%)",
        digits="Discount",
    )

    discount3 = fields.Float(
        "Disc. 3 (%)",
        digits="Discount",
    )

    _sql_constraints = [
        (
            "discount2_limit",
            "CHECK (discount2 <= 100.0)",
            "Discount 2 must be lower than 100%.",
        ),
        (
            "discount3_limit",
            "CHECK (discount3 <= 100.0)",
            "Discount 3 must be lower than 100%.",
        ),
    ]

    def _get_discounted_price_unit(self):
        # Include possible discounts 2 and 3
        price_unit = super()._get_discounted_price_unit()
        aggregated_discount = self._compute_aggregated_discount(self.discount)
        if aggregated_discount != self.discount:
            price_unit = self.price_unit * (1 - aggregated_discount / 100)
        return price_unit

    def _compute_aggregated_discount(self, base_discount):
        self.ensure_one()
        discounts = [base_discount]
        for discount_fname in self._get_multiple_discount_field_names():
            discounts.append(getattr(self, discount_fname, 0.0))
        return self._get_aggregated_multiple_discounts(discounts)

    @api.model
    def _apply_value_from_seller(self, seller):
        super()._apply_value_from_seller(seller)
        if not seller:
            return
        self.discount2 = seller.discount2
        self.discount3 = seller.discount3

    def _prepare_account_move_line(self, move=False):
        self.ensure_one()
        res = super()._prepare_account_move_line(move)
        res.update(
            {
                "discount2": self.discount2,
                "discount3": self.discount3,
            }
        )
        return res

    def _get_aggregated_multiple_discounts(self, discounts):
        discount_values = []
        for discount in discounts:
            discount_values.append(1 - (discount or 0.0) / 100.0)
        aggregated_discount = (
            1 - functools.reduce((lambda x, y: x * y), discount_values)
        ) * 100
        return aggregated_discount

    def _get_multiple_discount_field_names(self):
        return ["discount2", "discount3"]
