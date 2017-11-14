# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    minimum_po_amount = fields.Float(
        related='partner_id.minimum_po_amount',
        string="Purchase Minimum Amount",
        readonly=True,
    )

    @api.multi
    def _check_minimum_amount(self):
        for rec in self:
            po_amt_block = rec.env.ref('purchase_minimum_amount.'
                                       'minimum_amount_block_reason',
                                       raise_if_not_found=False)
            under_min = rec.amount_untaxed < rec.minimum_po_amount
            force_release = rec.env.context.get(
                'force_po_approval_block_release', False)
            if under_min and not rec.approval_block_id and not force_release:
                rec.approval_block_id = po_amt_block
            elif not under_min and rec.approval_block_id == po_amt_block:
                rec.approval_block_id = False
        return True

    @api.model
    def create(self, vals):
        po = super(PurchaseOrder, self).create(vals)
        po._check_minimum_amount()
        return po

    @api.multi
    def write(self, vals):
        res = super(PurchaseOrder, self).write(vals)
        for rec in self:
            if 'partner_id' in vals:
                rec._check_minimum_amount()
        return res


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.model
    def _check_minimum_amount_fields(self):
        return ['product_qty', 'price_unit']

    @api.model
    def create(self, vals):
        res = super(PurchaseOrderLine, self).create(vals)
        fields = self._check_minimum_amount_fields()
        if any(field in vals for field in fields):
            res.order_id._check_minimum_amount()
        return res

    @api.multi
    def write(self, vals):
        res = super(PurchaseOrderLine, self).write(vals)
        fields = self._check_minimum_amount_fields()
        for rec in self:
            if any(field in vals for field in fields):
                rec.order_id._check_minimum_amount()
        return res
