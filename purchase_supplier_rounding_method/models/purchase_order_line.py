# -*- coding: utf-8 -*-
# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.model
    def _calc_line_base_price(self, line):
        res = super(PurchaseOrderLine, self)._calc_line_base_price(line)
        if line.partner_id.supplier_rounding_method == 'round_net_price':
            return round(
                res, self.env['decimal.precision'].precision_get('Account'))
        else:
            return res
