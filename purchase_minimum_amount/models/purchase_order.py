# Copyright 2017 ForgeFlow S.L.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    minimum_po_amount = fields.Float(
        related="partner_id.minimum_po_amount",
        string="Purchase Minimum Amount",
    )

    @api.constrains("partner_id")
    def _check_minimum_amount(self):
        for rec in self:
            po_amt_block = rec.env.ref(
                "purchase_minimum_amount." "minimum_amount_block_reason",
                raise_if_not_found=False,
            )
            under_min = rec.amount_untaxed < rec.minimum_po_amount
            force_release = rec.env.context.get(
                "force_po_approval_block_release", False
            )
            if under_min and not rec.approval_block_id and not force_release:
                rec.approval_block_id = po_amt_block
            elif not under_min and rec.approval_block_id == po_amt_block:
                rec.approval_block_id = False
        return True


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.model
    def _check_minimum_amount_fields(self):
        """As we are adding a hook, we cannot use api.constrain"""
        return ["product_qty", "price_unit"]

    @api.model
    def create(self, vals):
        res = super(PurchaseOrderLine, self).create(vals)
        fields = self._check_minimum_amount_fields()
        if any(field in vals for field in fields):
            res.order_id._check_minimum_amount()
        return res

    def write(self, vals):
        res = super(PurchaseOrderLine, self).write(vals)
        fields = self._check_minimum_amount_fields()
        for rec in self:
            if any(field in vals for field in fields):
                rec.order_id._check_minimum_amount()
        return res
