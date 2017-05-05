# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from openerp import models, api


class PurchaseRequestLine(models.Model):
    _inherit = "purchase.request.line"

    @api.multi
    @api.depends('purchase_lines', 'purchase_lines.order_id.state')
    def _compute_purchase_state(self):
        super(PurchaseRequestLine, self)._compute_purchase_state()
        for rec in self:
            if rec.purchase_lines:
                if any([po_line.order_id.state == 'approved' for po_line in
                        rec.purchase_lines]):
                    rec.purchase_state = 'approved'
