# -*- coding: utf-8 -*-
# Copyright (c) 2016 Serv. Tecnol. Avanzados (http://www.serviciosbaeza.com)
#                    Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
#                    Andrius Preimantas <andrius@versada.lt>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields
import openerp.addons.decimal_precision as dp


class PricelistPartnerInfo(models.Model):
    _inherit = "pricelist.partnerinfo"

    discount = fields.Float(
        string='Discount (%)', digits_compute=dp.get_precision('Discount'))
