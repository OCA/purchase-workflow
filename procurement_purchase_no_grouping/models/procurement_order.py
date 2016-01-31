# -*- coding: utf-8 -*-
# © 2015 Pedro M. Baeza (http://http://www.serviciosbaeza.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, models


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.multi
    def make_po(self):
        obj = self.with_context(
            grouping=self.product_id.categ_id.procured_purchase_grouping)
        return super(ProcurementOrder, obj).make_po()
