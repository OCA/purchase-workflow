# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _action_see_purchase_order_attachments(self, products):
        domain = [
            "|",
            "&",
            ("res_model", "=", "product.product"),
            ("res_id", "in", products.ids),
            "&",
            ("res_model", "=", "product.template"),
            ("res_id", "in", products.mapped("product_tmpl_id").ids),
        ]
        res = self.env.ref("base.action_attachment").read()[0]
        ctx = {"create": False, "edit": False}
        res.update({"domain": domain, "context": ctx})
        return res

    def action_see_purchase_order_attachments(self):
        return self._action_see_purchase_order_attachments(
            self.mapped("order_line.product_id")
        )
