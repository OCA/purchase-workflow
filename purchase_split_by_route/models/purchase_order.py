# Copyright 2024 Akretion France (http://www.akretion.com/)
# @author: Mathieu Delva <mathieu.delva@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import re

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    default_route_id = fields.Many2one("stock.route", store=True)


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.model
    def _prepare_purchase_order_line_from_procurement(
        self, product_id, product_qty, product_uom, company_id, values, po
    ):
        vals = super()._prepare_purchase_order_line_from_procurement(
            product_id, product_qty, product_uom, company_id, values, po
        )
        origin = values["move_dest_ids"].origin
        if origin:
            origin = re.search(r"S\d+", origin)
        if origin:
            order_id = self.env["sale.order"].search([("name", "=", origin[0])])
            if order_id:
                po.default_route_id = order_id.route_id.id
        elif "orderpoint_id" in values:
            po.default_route_id = values["orderpoint_id"].route_id.id

        return vals
