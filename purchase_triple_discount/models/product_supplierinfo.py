# Copyright 2019 Tecnativa - David Vidal
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ProductSupplierInfo(models.Model):
    _name = "product.supplierinfo"
    _inherit = ["purchase.triple.discount.mixin", "product.supplierinfo"]
