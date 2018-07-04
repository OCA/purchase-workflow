# coding: utf-8
# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.model
    def _calc_line_base_price(self, line):
        """Overwrite Section to avoid bug in the order of inheritance
            of this function.
        """
        res = line.price_unit *\
            (1 - line.discount / 100.0) *\
            (1 - line.discount2 / 100.0) *\
            (1 - line.discount3 / 100.0)
        if line.partner_id.supplier_rounding_method == 'round_net_price':
            res = round(
                res, self.env['decimal.precision'].precision_get('Account'))
        return res
