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
            all_supplierinfo_ok = True
            if purchase.state in ("purchase", "done") and purchase.order_line.filtered(
                lambda l: not l.supplierinfo_ok
            ):
                all_supplierinfo_ok = False
            purchase.all_supplierinfo_ok = all_supplierinfo_ok

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
            supplierinfo_ok = True
            if line.state in (
                "purchase",
                "done",
            ) and not line.product_id.seller_ids.filtered(
                lambda s: s.name == line.order_id.partner_id.commercial_partner_id
            ):
                supplierinfo_ok = False
            line.supplierinfo_ok = supplierinfo_ok

    def action_create_missing_supplierinfo(self):
        return {
            "name": _("Supplierinfo"),
            "type": "ir.actions.act_window",
            "context": {
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
