# Copyright 2017-19 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _prepare_supplier_info(self, partner, line, price, currency):
        vals = super()._prepare_supplier_info(partner, line, price, currency)
        vals.update(
            {
                "discount2": line.discount2,
                "discount3": line.discount3,
            }
        )
        return vals


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
        price_unit = super()._get_discounted_price_unit()
        if self.discount2:
            price_unit *= 1 - self.discount2 / 100.0
        if self.discount3:
            price_unit *= 1 - self.discount3 / 100.0
        return price_unit

    @api.model
    def _apply_value_from_seller(self, seller):
        res = super()._apply_value_from_seller(seller)
        discounts = (
            {"discount2": seller.discount2, "discount3": seller.discount3}
            if seller
            else {"discount2": 0.00, "discount3": 0.00}
        )
        if not seller and not self.env.company.purchase_supplier_discount_real:
            return
        self.write(discounts)
        return res

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

    @api.model
    def _prepare_purchase_order_line_from_seller(self, seller):
        res = super()._prepare_purchase_order_line_from_seller(seller)
        if not res:
            return res
        res.update(
            {
                "discount2": seller.discount2,
                "discount3": seller.discount3,
            }
        )
