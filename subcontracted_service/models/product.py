# -*- coding: utf-8 -*-
# Author: Damien Crier
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    property_subcontracted_service = fields.Boolean(
        string="Subcontracted Service",
        company_dependent=True)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    def _need_procurement(self):
        for product in self:
            if (product.type == 'service' and
                    product.property_subcontracted_service):
                return True
        return super(ProductProduct, self)._need_procurement()
