# Copyright 2017 Today Mourad EL HADJ MIMOUNE @ Akretion
# Copyright 2020 Tecnativa - Manuel Calero
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def _search(self, domain, *args, **kwargs):
        if self.env.context.get("use_only_supplied_product"):
            restrict_supplier_id = self.env.context.get("restrict_supplier_id")
            seller = (
                self.env["res.partner"]
                .browse(restrict_supplier_id)
                .commercial_partner_id
            )
            supplierinfos = self.env["product.supplierinfo"].search(
                [("partner_id", "=", seller.id)]
            )
            extra_domain = [
                "|",
                ("product_tmpl_id", "in", supplierinfos.product_tmpl_id.ids),
                ("id", "in", supplierinfos.product_id.ids),
            ]

            domain = fields.Domain.AND([domain, extra_domain])

        return super()._search(domain, *args, **kwargs)
