# -*- coding: utf-8 -*-
# © 2016 Chafique DELLI @ Akretion
# © 2019 Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api, _


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.multi
    def _add_supplier_to_product(self):
        if not self._context.get("wizard_supplierinfo_confirm"):
            return super(PurchaseOrder, self)._add_supplier_to_product()
        else:
            # This is handled by the wizard
            return None

    @api.model
    def _check_product_supplierinfo(self):
        lines = []
        for line in self.order_line:
            suppinfo = False
            for seller in line.product_id.seller_ids:
                if (
                    self.partner_id == seller.name
                    or self.partner_id.commercial_partner_id == seller.name
                ):
                    suppinfo = seller
                    break
            if not suppinfo:
                lines.append(
                    (
                        0,
                        0,
                        {
                            "name": line.name,
                            "product_id": line.product_id.id,
                            "to_variant": True,
                        },
                    )
                )
        return lines

    @api.multi
    def button_confirm(self):
        self.ensure_one()
        lines_for_update = self._check_product_supplierinfo()
        if lines_for_update and self._context.get(
            "wizard_supplierinfo_confirm"
        ):
            if self.partner_id.commercial_partner_id:
                supplier_id = self.partner_id.commercial_partner_id
            else:
                supplier_id = self.partner_id
            ctx = {"default_wizard_line_ids": lines_for_update}
            add_supplierinfo_form = self.env.ref(
                "purchase_add_product_supplierinfo."
                "view_purchase_add_supplierinfo_form",
                False,
            )
            return {
                "name": _(
                    "Associate the supplier '%s' with the products "
                    "of this purchase order."
                )
                % supplier_id.name,
                "type": "ir.actions.act_window",
                "view_mode": "form",
                "res_model": "purchase.add.product.supplierinfo",
                "views": [(add_supplierinfo_form.id, "form")],
                "view_id": add_supplierinfo_form.id,
                "target": "new",
                "context": ctx,
            }
        else:
            return super(PurchaseOrder, self).button_confirm()
