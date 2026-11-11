# Copyright 2018-2019 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import models


class Orderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    def _quantity_in_progress(self):
        res = super()._quantity_in_progress()
        for prline in self.env["purchase.request.line"].search(
            [
                (
                    "request_id.state",
                    "in",
                    ("draft", "approved", "to_approve", "in_progress"),
                ),
                ("orderpoint_id", "in", self.ids),
                ("purchase_state", "=", False),
            ]
        ):
            res[prline.orderpoint_id.id] += prline.product_uom_id._compute_quantity(
                prline.product_qty, prline.orderpoint_id.product_uom, round=False
            )
        return res

    def _get_replenishment_order_notification(self):
        self.ensure_one()
        domain = [("orderpoint_id", "=", self.id)]
        if self.env.context.get("written_after"):
            domain.append(("create_date", ">=", self.env.context["written_after"]))
        request = self.env["purchase.request.line"].search(domain, order="id desc", limit=1).request_id
        if not request:
            return super()._get_replenishment_order_notification()
        return {
            "type": "ir.actions.client", "tag": "display_notification",
            "params": {
                "title": self.env._("Replenishment requested"),
                "message": "%s",
                "links": [{"label": request.display_name, "url": f"/odoo/action-purchase_request.purchase_request_form_action/{request.id}"}],
                "sticky": True,
            },
        }
