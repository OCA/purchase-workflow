# Copyright 2019 Tecnativa - David Vidal
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models


class ProductSupplierInfo(models.Model):
    _name = "product.supplierinfo"
    _inherit = ["product.supplierinfo", "triple.discount.mixin"]

    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        self.update(
            {
                field: self.partner_id[f"default_supplierinfo_{field}"]
                for field in self._get_multiple_discount_field_names()
            }
        )

    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        res.update(
            {
                field: self.partner_id[f"default_supplierinfo_{field}"]
                for field in self._get_multiple_discount_field_names()
            }
        )
        return res

    @api.model
    def _get_po_to_supplierinfo_synced_fields(self):
        res = super()._get_po_to_supplierinfo_synced_fields()
        res += self._get_multiple_discount_field_names()
        return res
