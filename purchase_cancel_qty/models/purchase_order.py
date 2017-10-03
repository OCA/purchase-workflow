# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class PurchaseOrder(models.Model):

    _inherit = 'purchase.order'

    @api.multi
    def button_approve(self, force=False):
        res = super(PurchaseOrder, self).button_approve(force=force)
        self._update_lines_ordered_qty()
        return res

    @api.multi
    def button_draft(self):
        res = super(PurchaseOrder, self).button_draft()
        self._reset_ordered_cancelled_qty()
        return res

    @api.multi
    def _update_lines_ordered_qty(self):
        for rec in self:
            rec.order_line._update_ordered_qty()

    @api.multi
    def _reset_ordered_cancelled_qty(self):
        for rec in self:
            rec.order_line._reset_ordered_cancelled_qty()
