# Copyright 2017-19 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _name = "purchase.order.line"
    _inherit = ["purchase.triple.discount.mixin", "purchase.order.line"]

    @api.depends("product_qty", "product_uom", "company_id")
    def _compute_price_unit_and_date_planned_and_name(self):
        res = super()._compute_price_unit_and_date_planned_and_name()
        self._compute_discounts()
        return res

    def _compute_discounts(self):
        for line in self:
            if not line.company_id or not line.product_id or line.invoice_lines:
                continue
            params = {"order_id": line.order_id}
            seller = line.product_id._select_seller(
                partner_id=line.partner_id,
                quantity=line.product_qty,
                date=line.order_id.date_order
                and line.order_id.date_order.date()
                or fields.Date.context_today(line),
                uom_id=line.product_uom,
                params=params,
            )
            if not seller:
                continue
            line.update(
                dict(
                    (fname, seller[fname] or 0.0)
                    for fname in self._get_multiple_discount_field_names()
                )
            )

    def _prepare_account_move_line(self, move=False):
        self.ensure_one()
        res = super()._prepare_account_move_line(move)
        res.update(
            dict(
                (fname, self[fname])
                for fname in self._get_multiple_discount_field_names()
            )
        )
        # TODO: Replace this when https://github.com/OCA/account-invoicing/pull/1638 is merged for:
        #       res.pop("discount")
        res["discount"] = res.pop("discount1")
        return res

    @api.model
    def _prepare_purchase_order_line(
        self, product_id, product_qty, product_uom, company_id, supplier, po
    ):
        res = super()._prepare_purchase_order_line(
            product_id, product_qty, product_uom, company_id, supplier, po
        )
        today = fields.Date.today()
        partner = supplier.partner_id
        uom_po_qty = product_uom._compute_quantity(
            product_qty, product_id.uom_po_id, rounding_method="HALF-UP"
        )
        seller = product_id.with_company(company_id)._select_seller(
            partner_id=partner,
            quantity=uom_po_qty,
            date=po.date_order and max(po.date_order.date(), today) or today,
            uom_id=product_id.uom_po_id,
        )
        res.update(
            dict(
                (fname, seller[fname] or 0.0)
                for fname in self._get_multiple_discount_field_names()
            )
        )
        res.pop("discount")
        return res
