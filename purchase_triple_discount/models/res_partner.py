# Copyright 2019 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields
from odoo.addons import decimal_precision as dp


class ResPartner(models.Model):
    _inherit = "res.partner"

    default_supplierinfo_discount2 = fields.Float(
        string='Default Supplier Discount 2 (%)',
        digits=dp.get_precision('Discount'),
        help="This value will be used as the default one, for each new "
             "supplierinfo line depending on that supplier.",
    )
    default_supplierinfo_discount3 = fields.Float(
        string='Default Supplier Discount 3 (%)',
        digits=dp.get_precision('Discount'),
        help="This value will be used as the default one, for each new "
             "supplierinfo line depending on that supplier.",
    )

    def button_apply_default_supplierinfo_discount2(self):
        for partner in self:
            self.env["product.supplierinfo"].search(
                [('name', '=', partner.id)]
            ).write({"discount2": partner.default_supplierinfo_discount2})

    def button_apply_default_supplierinfo_discount3(self):
        for partner in self:
            self.env["product.supplierinfo"].search(
                [('name', '=', partner.id)]
            ).write({"discount3": partner.default_supplierinfo_discount3})
