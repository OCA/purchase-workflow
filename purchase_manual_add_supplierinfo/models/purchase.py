# Copyright 2023 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import _, api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    all_supplierinfo_ok = fields.Boolean(
        string="supplierinfo is ok ?",
        compute="_compute_all_supplierinfo_ok",
        store=True,
    )

    @api.depends("state", "order_line.supplierinfo_ok")
    def _compute_all_supplierinfo_ok(self):
        for purchase in self:
            purchase.all_supplierinfo_ok = all(
                purchase.order_line.mapped("supplierinfo_ok")
            )

    def update_supplierinfo(self):
        return (
            self.env["product.supplierinfo"]
            .with_context(update_from_po_id=self.id)
            .update_from_purchase()
        )

    def _add_supplier_to_product(self):
        return True


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    supplierinfo_ok = fields.Boolean(
        string="supplierinfo is ok ?", compute="_compute_supplierinfo_ok", store=True
    )

    @api.depends("state", "product_id.seller_ids")
    def _compute_supplierinfo_ok(self):
        for line in self:
            if line.state not in ("purchase", "done") or not line.product_id:
                line.supplierinfo_ok = True
            else:
                line.supplierinfo_ok = bool(
                    line.product_id._select_seller(
                        line.order_id.partner_id.commercial_partner_id,
                        quantity=None,
                    )
                )

    def action_create_missing_supplierinfo(self):
        return {
            "name": _("Supplierinfo"),
            "type": "ir.actions.act_window",
            "context": {
                "create_temporary_supplier_info": True,
                "update_from_po_id": self._context.get("update_from_po_id"),
                "update_from_po_line_id": self.id,
                "visible_product_tmpl_id": False,
                "default_product_tmpl_id": self.product_id.product_tmpl_id.id,
                "default_product_id": self.product_id.id,
                "default_price": self.price_unit,
                "default_name": self.partner_id.commercial_partner_id.id,
                "default_min_qty": 0.0,
                "default_delay": 1.0,
            },
            "view_mode": "form",
            "res_model": "product.supplierinfo",
            "view_id": False,
            "views": [(False, "form")],
            "target": "new",
        }
