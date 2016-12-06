# -*- coding: utf-8 -*-
# Copyright 2015 AvanzOsc (http://www.avanzosc.es)
# Copyright 2015-2016 - Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from openerp import models, api


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.multi
    def make_po(self):
        obj = self.with_context(
            grouping=self.product_id.categ_id.procured_purchase_grouping,
        )
        return super(ProcurementOrder, obj).make_po()
