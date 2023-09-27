# Copyright 2021 Akretion - www.akretion.com.br -
# @author  Magno Costa <magno.costa@akretion.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    # Used in wizard view to show only products with has BoM.
    # Field must be stored to be used in domain, without it the LOG return:
    # ERROR db odoo.osv.expression: Non-stored
    # field product.product.bom_count cannot be searched.
    bom_count = fields.Integer(store=True)
