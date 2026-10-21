# Copyright 2026 Ecosoft Co., Ltd. (<http://ecosoft.co.th>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_compare, float_round


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    discount_fixed = fields.Float(
        string="Discount (Fixed)",
        digits="Product Price",
        help="Fixed amount discount.",
    )

    @api.constrains("discount_fixed", "discount")
    def _check_discounts(self):
        """Check that the fixed discount and the discount percentage are consistent."""
        for line in self:
            if line.discount_fixed and line.discount:
                currency = line.currency_id
                calculated_fixed_discount = float_round(
                    line._get_discount_from_fixed_discount(),
                    precision_rounding=currency.rounding,
                )

                if (
                    float_compare(
                        calculated_fixed_discount,
                        line.discount,
                        precision_rounding=currency.rounding,
                    )
                    != 0
                ):
                    raise ValidationError(
                        self.env._(
                            "The fixed discount %(fixed)s does not match the calculated"
                            "discount %(discount)s %%."
                            "Please correct one of the discounts.",
                            fixed=line.discount_fixed,
                            discount=line.discount,
                        )
                    )

    def _prepare_base_line_for_taxes_computation(self, **kwargs):
        """Prior to calculating the tax toals for a line, update the discount value
        used in the tax calculation to the full float value. Otherwise, we get rounding
        errors in the resulting calculated totals.

        For example:
            - price_unit = 750.0
            - discount_fixed = 100.0
            - discount = 13.33
            => price_subtotal = 650.03

        :return: A python dictionary.
        """
        self.ensure_one()

        # Accurately pass along the fixed discount amount to the tax computation method.
        if self.discount_fixed:
            return self.env["account.tax"]._prepare_base_line_for_taxes_computation(
                self,
                **{
                    "tax_ids": self.taxes_id,
                    "quantity": self.product_qty,
                    "partner_id": self.order_id.partner_id,
                    "currency_id": self.order_id.currency_id
                    or self.order_id.company_id.currency_id,
                    "rate": self.order_id.currency_rate,
                    "discount": self._get_discount_from_fixed_discount(),
                    **kwargs,
                },
            )

        return super()._prepare_base_line_for_taxes_computation(**kwargs)

    @api.onchange("discount_fixed", "price_unit")
    def _onchange_discount_fixed(self):
        if self.discount_fixed:
            self.discount = self._get_discount_from_fixed_discount()

    def _get_discount_from_fixed_discount(self):
        """Calculate the discount percentage from the fixed discount amount."""
        self.ensure_one()
        if not self.discount_fixed:
            return 0.0

        return (
            (self.price_unit != 0)
            and ((self.discount_fixed) / self.price_unit) * 100
            or 0.00
        )

    def _prepare_account_move_line(self, move=False):
        res = super()._prepare_account_move_line(move)
        res.update({"discount_fixed": self.discount_fixed})
        return res
