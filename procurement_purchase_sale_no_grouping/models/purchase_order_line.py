# Copyright 2021 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.model
    def search(self, domain, offset=0, limit=None, order=None):
        # As of 19.0, sale_purchase looks for an existing RFQ to reuse through
        # ``purchase.order.line`` (see ``_purchase_service_match_purchase_order``)
        # instead of ``purchase.order``. Returning an empty recordset here when
        # the dedicated context key is set forces a brand new purchase order to
        # be created, which is what the "No order grouping" option expects.
        if self.env.context.get("search_purchase_no_grouping", False):
            return self.browse()
        return super().search(domain, offset=offset, limit=limit, order=order)
