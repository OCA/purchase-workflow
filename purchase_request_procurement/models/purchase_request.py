# -*- coding: utf-8 -*-
# Copyright 2016-2017 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo import api, models


class PurchaseRequest(models.Model):

    _inherit = 'purchase.request'

    @api.multi
    def button_rejected(self):
        res = super(PurchaseRequest, self).button_rejected()
        for pr in self:
            pr.line_ids.mapped('procurement_id').cancel()
        return res
