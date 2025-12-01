
# Copyright 2017-19 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _name = "purchase.order.line"
    _inherit = ["purchase.order.line", "triple.discount.mixin"]

    # Redefine discount as computed to show aggregated discount
    discount = fields.Float(
        compute="_compute_discount",
        store=True,
        readonly=True,
    )

    discounted_unit_price = fields.Monetary(
        string="Discounted Unit Price",
        compute="_compute_discounted_unit_price",
        store=True,
        help="Final unit price after applying all three discounts in cascade",
    )

    @api.depends("discount1", "discount2", "discount3")
    def _compute_discount(self):
        """Compute the equivalent single discount from the three cascading discounts."""
        for line in self:
            factor = 1.0
            for discount in [line.discount1, line.discount2, line.discount3]:
                if discount:
                    factor *= (1 - discount / 100.0)
            line.discount = (1 - factor) * 100.0

    # Override to add triple discount dependencies
    @api.depends("discount1", "discount2", "discount3")
    def _compute_amount(self):
        """Override to ensure amount is recalculated when triple discounts change."""
        return super()._compute_amount()

    @api.depends("price_unit", "discount1", "discount2", "discount3")
    def _compute_discounted_unit_price(self):
        """
        Compute the final discounted unit price by applying three discounts in cascade.
        Formula:
        - discounted_price_1 = price_unit * (1 - discount1/100)
        - discounted_price_2 = discounted_price_1 * (1 - discount2/100)
        - discounted_price_3 = discounted_price_2 * (1 - discount3/100)
        """
        for line in self:
            price = line.price_unit
            # Apply first discount
            if line.discount1:
                price = price * (1 - line.discount1 / 100)
            # Apply second discount on the already discounted price
            if line.discount2:
                price = price * (1 - line.discount2 / 100)
            # Apply third discount on the already discounted price
            if line.discount3:
                price = price * (1 - line.discount3 / 100)
            line.discounted_unit_price = price

    def _convert_to_tax_base_line_dict(self):
        """
        Override to ensure the cascading discounted price is used in tax calculation.
        This directly affects the price_subtotal computation.
        """
        vals = super()._convert_to_tax_base_line_dict()
        vals["price_unit"] = self._get_discounted_price_unit()
        return vals

    def _get_discounted_price_unit(self):
        """
        Override to implement cascading triple discount calculation.
        Applies discount1, then discount2, then discount3 in sequence.
        """
        self.ensure_one()
        price = self.price_unit
        # Apply first discount
        if self.discount1:
            price = price * (1 - self.discount1 / 100)
        # Apply second discount on the already discounted price
        if self.discount2:
            price = price * (1 - self.discount2 / 100)
        # Apply third discount on the already discounted price
        if self.discount3:
            price = price * (1 - self.discount3 / 100)
        return price

    @api.model
    def _apply_value_from_seller(self, seller):
        super()._apply_value_from_seller(seller)
        if not seller:
            return
        self.update(
            {
                field: seller[field]
                for field in self._get_multiple_discount_field_names()
            }
        )

    def _prepare_account_move_line(self, move=False):
        self.ensure_one()
        res = super()._prepare_account_move_line(move)
        res.update(
            {field: self[field] for field in self._get_multiple_discount_field_names()}
        )
        return res

    def write(self, vals):
        # Prevent the mixin from converting discount back to discount1.
        # In triple discount mode, 'discount' is a computed field from discount1/2/3,
        # so we should never allow it to be written and converted back.
        # Remove 'discount' from vals to prevent mixin's conversion logic.
        if "discount" in vals:
            vals = vals.copy()
            vals.pop("discount")

        res = super().write(vals)

        discount_fields = ["discount1", "discount2", "discount3"]
        if any(field in vals for field in discount_fields) or "price_unit" in vals:
            for line in self.filtered(lambda l: l.order_id.state == "purchase"):
                # Avoid updating kit components' stock.move
                moves = line.move_ids.filtered(
                    lambda s: s.state not in ("cancel", "done")
                    and s.product_id == line.product_id
                )
                moves.write({"price_unit": line._get_discounted_price_unit()})
        return res
