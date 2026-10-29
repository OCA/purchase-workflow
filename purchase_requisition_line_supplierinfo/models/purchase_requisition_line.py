# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import fields, models


class PurchaseRequisitionLine(models.Model):
    _inherit = "purchase.requisition.line"

    delay = fields.Integer(
        string="Lead Time",
        default=1,
        help="Days between the confirmation of a purchase order placed under "
        "this agreement and the receipt of the products. Written onto the "
        "vendor pricelist line created when the agreement is confirmed.",
    )
    min_qty = fields.Float(
        string="Minimum Quantity",
        digits="Product Unit",
        default=1.0,
        help="Minimum quantity the vendor accepts on a purchase order placed "
        "under this agreement, in the unit of the agreement line. Written onto "
        "the vendor pricelist line created when the agreement is confirmed.",
    )

    def _get_supplier_info_terms(self):
        self.ensure_one()
        return {"delay": self.delay, "min_qty": self.min_qty}

    def _create_supplier_info(self):
        self.ensure_one()
        existing = self.supplier_info_ids
        res = super()._create_supplier_info()
        created = self.supplier_info_ids - existing
        if created:
            created.sudo().write(self._get_supplier_info_terms())
        return res

    def write(self, vals):
        res = super().write(vals)
        if {"delay", "min_qty"} & vals.keys():
            for line in self.filtered("supplier_info_ids"):
                line.supplier_info_ids.sudo().write(line._get_supplier_info_terms())
        return res

    def _prepare_purchase_order_line(
        self, name, product_qty=0.0, price_unit=0.0, taxes_ids=False
    ):
        vals = super()._prepare_purchase_order_line(
            name, product_qty=product_qty, price_unit=price_unit, taxes_ids=taxes_ids
        )
        if self.requisition_id.requisition_type == "blanket_order" and vals.get(
            "date_planned"
        ):
            vals["date_planned"] = fields.Datetime.to_datetime(
                vals["date_planned"]
            ) + timedelta(days=self.delay)
        return vals
