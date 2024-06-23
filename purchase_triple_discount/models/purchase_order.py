# Copyright 2017-19 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class PurchaseOrderLine(models.Model):
    _name = "purchase.order.line"
    _inherit = ["purchase.order.line", "triple.discount.mixin"]

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
