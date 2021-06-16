# Copyright 2016 Nicola Malcontenti - Agile Business Group
# Copyright 2021 Alfredo Zamora - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    product_customer_code = fields.Char(
        "Product Customer Code", compute="_compute_product_customer_code"
    )

    def _compute_product_customer_code(self):
        product_customerinfo_obj = self.env["product.customerinfo"]
        for line in self:
            code_id = product_customerinfo_obj.browse()
            partner = line.partner_id
            product = line.product_id
            if product and partner:
                code_id = product_customerinfo_obj.search(
                    [("name", "=", partner.id)]
                    + [
                        "|",
                        ("product_id", "=", product.id),
                        "&",
                        ("product_tmpl_id", "=", product.product_tmpl_id.id),
                        ("product_id", "=", False),
                    ],
                    limit=1,
                )
            line.product_customer_code = code_id.product_code or ""
