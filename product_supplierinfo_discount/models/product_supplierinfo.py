# -*- coding: utf-8 -*-
# © 2014 Serv. Tecnol. Avanzados (http://www.serviciosbaeza.com)
#        Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
# © 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp


class ProductSupplierInfo(models.Model):
    _inherit = 'product.supplierinfo'

    discount = fields.Float(
        string='Discount (%)', digits_compute=dp.get_precision('Discount'))

    @api.onchange('name')
    @api.multi
    def onchange_name(self):
        for supplierinfo in self.filtered('name'):
            supplierinfo.discount =\
                supplierinfo.name.default_supplierinfo_discount
