# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# Copyright 2014-2019 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models


class ProductSupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    discount = fields.Float(string="Discount (%)", digits="Discount")

    @api.onchange("name")
    def onchange_name(self):
        """ Apply the default supplier discount of the selected supplier """
        for supplierinfo in self.filtered("name"):
            supplierinfo.discount = supplierinfo.name.default_supplierinfo_discount

    @api.model
    def _get_po_to_supplierinfo_synced_fields(self):
        """Overwrite this method for adding other fields to be synchronized
        with product.supplierinfo.
        """
        return ["discount"]

    @api.model_create_multi
    def create(self, vals_list):
        """Insert discount (or others) from context from purchase.order's
        _add_supplier_to_product method"""
        for vals in vals_list:
            product_tmpl_id = vals.get("product_tmpl_id")
            po_line_map = self.env.context.get("po_line_map", {})
            if product_tmpl_id in po_line_map:
                po_line = po_line_map[product_tmpl_id]
                for field in self._get_po_to_supplierinfo_synced_fields():
                    if not vals.get(field):
                        vals[field] = po_line[field]
        return super().create(vals_list)
