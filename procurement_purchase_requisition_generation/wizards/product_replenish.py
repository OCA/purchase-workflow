# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ProductReplenish(models.TransientModel):
    _inherit = "product.replenish"

    def _get_record_to_notify(self, date):
        requisition_line = self.env["purchase.requisition.line"].search(
            [("write_date", ">=", date)], limit=1
        )
        return requisition_line or super()._get_record_to_notify(date)

    def _get_replenishment_order_notification_link(self, requisition_line):
        if requisition_line._name == "purchase.requisition.line":
            action = self.env.ref(
                "procurement_purchase_requisition_generation.action_purchase_requisition_form"
            )
            r = requisition_line.requisition_id
            return [
                {
                    "label": r.display_name,
                    "url": f"#action={action.id}&id={r.id}&model={r._name}",
                }
            ]
        return super()._get_replenishment_order_notification_link(requisition_line)
