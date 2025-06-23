# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    purchase_only_by_packaging = fields.Boolean(
        string="Only purchase by packaging",
        company_dependent=True,
        default=False,
        help="Restrict the usage of this product on purchase order lines without "
        "packaging defined",
    )

    min_purchasable_qty = fields.Float(
        compute="_compute_template_min_purchasable_qty",
        help=(
            "Minimum purchasable quantity, according to the available packagings, "
            "if Only Purchase by Packaging is set."
        ),
    )

    @api.depends(
        "purchase_only_by_packaging",
        "uom_id.factor",
        "product_variant_ids.min_purchasable_qty",
    )
    def _compute_template_min_purchasable_qty(self):
        for record in self:
            record.min_purchasable_qty = 0.0
            if len(record.product_variant_ids) == 1:
                # Pick the value from the variant if there's only 1
                record.min_purchasable_qty = (
                    record.product_variant_ids.min_purchasable_qty
                )

    @api.constrains("purchase_only_by_packaging", "purchase_ok")
    def _check_purchase_only_by_packaging_purchase_ok(self):
        for product in self:
            if product.purchase_only_by_packaging and not product.purchase_ok:
                raise ValidationError(
                    _(
                        "Product %s cannot be defined to be purchased only by "
                        "packaging if it cannot be purchased."
                    )
                    % product.name
                )

    @api.constrains("purchase_only_by_packaging", "packaging_ids")
    def _check_purchase_only_by_packaging_can_be_purchased_packaging_ids(self):
        for product in self:
            if product.purchase_only_by_packaging:
                if (
                    # Product template only condition
                    len(product.product_variant_ids) == 1
                    and not any(pack.can_be_purchased for pack in product.packaging_ids)
                    # Product variants condition
                    or len(product.product_variant_ids) > 1
                    and not any(
                        pack.can_be_purchased
                        for pack in product.product_variant_ids.mapped("packaging_ids")
                    )
                ):
                    raise ValidationError(
                        _(
                            "Product %s cannot be defined to be purchased only by "
                            "packaging if it does not have any packaging that "
                            "can be purchased defined."
                        )
                        % product.name
                    )
