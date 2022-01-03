# Copyright 2017-19 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    # adding discount2 and discount3 to depends
    @api.depends("discount2", "discount3")
    def _compute_amount(self):
        super()._compute_amount()

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
        price_unit = super()._get_discounted_price_unit()
        if self.discount2:
            price_unit *= 1 - self.discount2 / 100.0
        if self.discount3:
            price_unit *= 1 - self.discount3 / 100.0
        return price_unit

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
