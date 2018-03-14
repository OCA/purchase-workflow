# -*- coding: utf-8 -*-
# Copyright 2015 AvanzOsc (http://www.avanzosc.es)
# Copyright 2015-2016 - Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, api


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.multi
    def make_po(self):
        grouping = self.product_id.categ_id.procured_purchase_grouping
        obj = self.with_context(grouping=grouping)
        res = super(ProcurementOrder, obj).make_po()
        # Force triggers re-execution because search has block it
        if grouping == 'line':
            for po_line in self.browse(res).mapped('purchase_line_id'):
                po_line.write(po_line._convert_to_write(
                    po_line._convert_to_cache(po_line.read()[0])))
        return res
