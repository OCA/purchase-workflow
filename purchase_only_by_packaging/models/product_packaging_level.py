# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, exceptions, models


class ProductPackagingLevel(models.Model):
    _inherit = "product.packaging.level"

    @api.constrains("can_be_purchased")
    def _check_purchase_only_by_packaging_can_be_purchased_packaging_ids(self):
        for record in self:
            if record.can_be_purchased:
                continue
            products = record.packaging_ids.product_id
            templates = products.product_tmpl_id
            try:
                templates._check_purchase_only_by_packaging_can_be_purchased_packaging_ids()
            except exceptions.ValidationError as e:
                raise exceptions.ValidationError(
                    _(
                        'Packaging level "{}" must stay with "Can be purchased",'
                        ' at least one product configured as "purchase only'
                        ' by packaging" is using it.'
                    ).format(record.display_name)
                ) from e
