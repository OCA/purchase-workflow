# -*- coding: utf-8 -*-
# Copyright 2015 Avanzosc(http://www.avanzosc.es)
# Copyright 2015 Tecnativa (http://www.tecnativa.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class Product(models.Model):
    _inherit = 'product.product'

    @api.multi
    def need_procurement(self):
        for product in self:
            if product.type == 'service':
                return True
        return super(Product, self).need_procurement()
