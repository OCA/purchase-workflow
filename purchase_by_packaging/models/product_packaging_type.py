# Copyright 2021 Ametras
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import _, api, exceptions, fields, models


class ProductPackagingType(models.Model):
    _inherit = "product.packaging.type"

    can_be_purchased = fields.Boolean(
        string="Can be purchased", default=True, index=True
    )
    packaging_ids = fields.One2many(
        comodel_name="product.packaging", inverse_name="packaging_type_id"
    )

    @api.constrains("can_be_purchased")
    def _check_purchase_only_by_packaging_can_be_purchased_ids(self):
        for record in self:
            if record.can_be_purchased:
                continue
            products = record.packaging_ids.product_id
            templates = products.product_tmpl_id
            try:
                templates._check_purchase_only_by_packaging_can_be_purchased_packaging_ids()
            except exceptions.ValidationError:
                raise exceptions.ValidationError(
                    _(
                        'Packaging type "{}" must stay with "Can be purchased",'
                        ' at least one product configured as "purchase only'
                        ' by packaging" is using it.'
                    ).format(record.display_name)
                )
