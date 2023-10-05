# Copyright 2023 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import _, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    all_supplierinfo_ok = fields.Boolean(string="supplierinfo is ok ?")

    def _check_supplierinfo(self):
        for purchase in self:
            all_supplierinfo_ok = True
            for line in purchase.order_line:
                l_supplierinfo_ok = False
                if line.product_id.seller_ids.filtered(
                    lambda s: s.name == purchase.partner_id.commercial_partner_id
                ):
                    l_supplierinfo_ok = True
                line.supplierinfo_ok = l_supplierinfo_ok
            if purchase.order_line.filtered(lambda l: not l.supplierinfo_ok):
                all_supplierinfo_ok = False
            purchase.all_supplierinfo_ok = all_supplierinfo_ok

    def button_confirm(self):
        self._check_supplierinfo()
        return super().button_confirm()

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

    supplierinfo_ok = fields.Boolean(string="supplierinfo is ok ?")

    def create_missing_supplierinfo(self):
        update_from_po_line_id = False
        if not self._context.get("update_from_po_id", False):
            update_from_po_line_id = self.id
        return {
            "name": _("Supplierinfo"),
            "type": "ir.actions.act_window",
            "context": {
                "update_from_po_id": self._context.get("update_from_po_id", False),
                "update_from_po_line_id": update_from_po_line_id,
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
