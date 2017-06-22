# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.multi
    def _prepare_purchase_order_line(self, po, supplier):
        """When creating PO lines mantain as scheduled date the one specified
        in the procurement."""
        res = super(ProcurementOrder, self)._prepare_purchase_order_line(
            po, supplier)
        res['date_planned'] = self.date_planned
        return res
