# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.multi
    def make_po(self):
        obj = self.with_context(
            grouping=self.product_id.categ_id.procured_purchase_grouping)
        return super(ProcurementOrder, obj).make_po()
