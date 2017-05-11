# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        account_analytic_id = self._context.get('account_analytic_id')
        if account_analytic_id:
            args.append((('order_line.account_analytic_id', '=',
                          account_analytic_id)))
        return super(PurchaseOrder, self).search(args, offset=offset,
                                                 limit=limit, order=order,
                                                 count=count)
