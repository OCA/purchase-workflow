# Copyright 2019 Aleph Objects, Inc.
# Copyright 2019 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

from odoo import fields, models


class ProductUsage(models.Model):
    _name = "purchase.product.usage"
    _description = "Product Usage"

    name = fields.Char(string="Description", required=True)
    code = fields.Char(string="Code")
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.user.company_id,
    )
    active = fields.Boolean(default=True)
    account_id = fields.Many2one(
        comodel_name="account.account",
        string="Account",
        help="Expense account for vendor bills",
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        domain=[("type", "in", ["consu", "service"])],
        string="Default Product",
        help="Purchase this product by default",
    )

    def name_get(self):
        result = super(ProductUsage, self).name_get()
        new_result = []
        for usage in result:
            rec = self.browse(usage[0])
            if rec.code:
                name = "[{}] {}".format(rec.code, usage[1])
            else:
                name = usage[1]
            new_result.append((rec.id, name))
        return new_result
