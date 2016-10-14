# -*- coding: utf-8 -*-
# (c) 2010-2013 Elio Corp. - Yannick Gouin
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields


class ProductSupplierinfo(models.Model):
    _inherit = 'product.supplierinfo'

    delay = fields.Integer(group_operator='avg')
