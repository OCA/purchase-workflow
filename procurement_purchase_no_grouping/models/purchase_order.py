# Copyright 2015 AvanzOsc (http://www.avanzosc.es)
# Copyright 2018 Tecnativa - Carlos Dauden
# Copyright 2015-2021 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _find_candidate(
        self,
        product_id,
        product_qty,
        product_uom,
        location_id,
        name,
        origin,
        company_id,
        values,
    ):
        """If not grouping by line, we should make an exception when you update an
        existing sales order line, so we filter a bit more by procurement group.

        NOTE: This makes that if you manually assign the same procurement group to
        several different sales orders, the grouping will be done no matter the grouping
        criteria, but this is the only way to do it without having to put a lot of glue
        modules, and on standard operation mode, procurement groups are not reused
        between sales orders.
        """
        obj = self
        if values.get("grouping") == "line":
            obj = self.filtered(lambda x: x.order_id.group_id == values.get("group_id"))
        return super(PurchaseOrderLine, obj)._find_candidate(
            product_id,
            product_qty,
            product_uom,
            location_id,
            name,
            origin,
            company_id,
            values,
        )
