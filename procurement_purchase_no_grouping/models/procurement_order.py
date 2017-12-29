# -*- coding: utf-8 -*-
# Copyright 2017 OdooMRP team
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import models, api


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.multi
    def make_po(self):
        obj = self.with_context(
            grouping=self.product_id.categ_id.procured_purchase_grouping,
            origin=self.origin,
        )
        return super(ProcurementOrder, obj).make_po()
