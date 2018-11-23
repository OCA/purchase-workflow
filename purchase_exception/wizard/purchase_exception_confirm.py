# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com)
# Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class PurchaseExceptionConfirm(models.TransientModel):
    _name = 'purchase.exception.confirm'
    _inherit = ['exception.rule.confirm']

    related_model_id = fields.Many2one('purchase.order', 'Purchase')

    @api.multi
    def action_confirm(self):
        self.ensure_one()
        if self.ignore:
            self.related_model_id.button_draft()
            self.related_model_id.ignore_exception = True
            self.related_model_id.button_confirm()
        return super(PurchaseExceptionConfirm, self).action_confirm()
