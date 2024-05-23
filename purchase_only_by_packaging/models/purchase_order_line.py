# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import _, api, models
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


class PurchaseOrderLine(models.Model):

    _inherit = "purchase.order.line"

    @api.constrains(
        "product_id", "product_packaging_id", "product_packaging_qty", "product_qty"
    )
    def _check_product_packaging_purchase_only_by_packaging(self):
        for line in self:
            if not line.product_id.purchase_only_by_packaging:
                continue

            if (
                not line.product_packaging_id
                or float_compare(
                    line.product_packaging_qty,
                    int(line.product_packaging_qty),
                    precision_digits=2,
                )
                != 0
            ):
                raise ValidationError(
                    _(
                        "Product %s can only be purchased with a packaging and a "
                        "packaging quantity."
                    )
                    % line.product_id.name
                )

    def _force_qty_with_package(self):
        """

        :return:
        """
        self.ensure_one()
        qty = self.product_id._convert_purchase_packaging_qty(
            self.product_qty, self.product_uom, packaging=self.product_packaging_id
        )
        self.product_qty = qty
        return True

    @api.onchange("product_qty")
    def _onchange_product_qty(self):
        self._force_qty_with_package()
