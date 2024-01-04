# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# Copyright 2014-2019 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models


class ProductSupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    discount = fields.Float(string="Discount (%)", digits="Discount")

    @api.onchange("name")
    def onchange_name(self):
        """Apply the default supplier discount of the selected supplier"""
        for supplierinfo in self.filtered("name"):
            supplierinfo.discount = supplierinfo.name.default_supplierinfo_discount
