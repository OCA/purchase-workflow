# Copyright 2017-19 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import functools

from odoo import api, fields, models


class TripleDiscountMixin(models.AbstractModel):
    _name = "purchase.triple.discount.mixin"

    discount = fields.Float(
        compute="_compute_discount",
        store=True,
    )
    discount1 = fields.Float(
        string="Disc. 1 (%)",
        digits="Discount",
        readonly=False,
    )

    discount2 = fields.Float(
        string="Disc. 2 (%)",
        digits="Discount",
        readonly=False,
    )
    discount3 = fields.Float(
        string="Disc. 3 (%)",
        digits="Discount",
        readonly=False,
    )

    _sql_constraints = [
        (
            "discount1_limit",
            "CHECK (discount1 <= 100.0)",
            "Discount 1 must be lower than 100%.",
        ),
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

    @api.depends(lambda self: self._get_multiple_discount_field_names())
    def _compute_discount(self):
        for record in self:
            record.discount = record._get_aggregated_discount_from_values(
                {
                    fname: record[fname]
                    for fname in record._get_multiple_discount_field_names()
                }
            )

    def _get_aggregated_discount_from_values(self, values):
        discount_fnames = self._get_multiple_discount_field_names()
        discounts = []
        for discount_fname in discount_fnames:
            discounts.append(values.get(discount_fname) or 0.0)
        return self._get_aggregated_multiple_discounts(discounts)

    @staticmethod
    def _get_multiple_discount_field_names():
        return ["discount1", "discount2", "discount3"]

    @staticmethod
    def _get_aggregated_multiple_discounts(discounts):
        discount_values = []
        for discount in discounts:
            discount_values.append(1 - (discount or 0.0) / 100.0)
        aggregated_discount = (
            1 - functools.reduce((lambda x, y: x * y), discount_values)
        ) * 100
        return aggregated_discount
