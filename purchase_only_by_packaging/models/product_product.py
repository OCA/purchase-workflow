# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.tools import float_compare, float_round


class ProductProduct(models.Model):
    _inherit = "product.product"

    min_purchasable_qty = fields.Float(
        compute="_compute_variant_min_purchasable_qty",
        help=(
            "Minimum purchasable quantity, according to the available packagings, "
            "if Only Purchase by Packaging is set."
        ),
    )

    @api.depends(
        "purchase_only_by_packaging",
        "packaging_ids.qty",
        "packaging_ids.can_be_purchased",
    )
    def _compute_variant_min_purchasable_qty(self):
        for record in self:
            record.min_purchasable_qty = 0.0
            if record.purchase_only_by_packaging and record.packaging_ids:
                purchasable_pkgs = record.packaging_ids.filtered(
                    lambda p: p.can_be_purchased
                )
                record.min_purchasable_qty = fields.first(
                    purchasable_pkgs.sorted(lambda p: p.qty)
                ).qty

    def _convert_purchase_packaging_qty(self, qty, uom, packaging):
        """
        Convert the given qty with given UoM to the packaging uom.
        To do that, first transform the qty to the reference UoM and then
        transform using the packaging UoM.
        The given qty is not updated if the product has purchase_only_by_packaging
        set to False or if the packaging is not set.
        :param qty: float
        :return: float
        """
        if not self or not packaging:
            return qty
        self.ensure_one()
        if self.purchase_only_by_packaging and packaging.force_purchase_qty:
            q = self.uom_id._compute_quantity(packaging.qty, uom)
            if (
                qty
                and q
                and float_compare(
                    qty / q,
                    float_round(qty / q, precision_rounding=1.0),
                    precision_rounding=0.001,
                )
                != 0
            ):
                qty = qty - (qty % q) + q
        return qty
