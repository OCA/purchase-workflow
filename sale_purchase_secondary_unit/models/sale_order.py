# Copyright 2023 Tecnativa - Carlos Dauden
# Copyright 2023 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_cancel(self):
        # When a SO linked to a purchase order is cancelled we must update the
        # secondary_uom_qty on po line
        return super(
            SaleOrder, self.with_context(cancelled_so_lines=self.order_line.ids)
        ).action_cancel()


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _prepare_procurement_values(self, group_id=False):
        values = super()._prepare_procurement_values(group_id)
        values["secondary_uom_id"] = self.secondary_uom_id.id
        values["secondary_uom_qty"] = self.secondary_uom_qty
        return values
