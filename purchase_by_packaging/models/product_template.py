# Copyright 2021 Ametras
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    purchase_only_by_packaging = fields.Boolean(
        string="Only purchase by packaging",
        default=False,
        help="Restrict the usage of this product on purchase order lines without "
        "packaging defined",
    )

    @api.constrains("purchase_only_by_packaging", "purchase_ok")
    def _check_purchase_only_by_packaging_purchase_ok(self):
        for product in self:
            if product.purchase_only_by_packaging and not product.purchase_ok:
                raise ValidationError(
                    _(
                        "Product %s cannot be defined to be purchase only by "
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
                            "Product %s cannot be defined to be purchase only by "
                            "packaging if it does not have any packaging that "
                            "can be purchase defined."
                        )
                        % product.name
                    )

    @api.onchange("purchase_ok")
    def _change_purchase_ok(self):
        if not self.purchase_ok and self.purchase_only_by_packaging:
            self.purchase_only_by_packaging = False
