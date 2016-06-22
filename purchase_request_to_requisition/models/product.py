# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L.
# - Jordi Ballester Alomar
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.multi
    def _check_request_requisition(self):
        for product in self:
            if product.purchase_request and product.purchase_requisition:
                return False
        return True

    _constraints = [
        (_check_request_requisition,
         'Only one selection of Purchase Request or Call for Bids allowed',
         ['purchase_request', 'purchase_requisition'])]
