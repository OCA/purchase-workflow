# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    require_wa = fields.Boolean(compute="_compute_require_wa")
    wa_id = fields.Many2one(
        comodel_name="work.acceptance",
        string="WA Reference",
        copy=False,
        readonly=True,
        domain=lambda self: [
            ("state", "=", "accept"),
            ("purchase_id", "=", self._context.get("active_id")),
        ],
        help="To control quantity and unit price of the vendor bill, to be "
        "according to the quantity and unit price of the work acceptance.",
    )

    def _compute_require_wa(self):
        for rec in self:
            enforce_wa = self.env.user.has_group(
                "purchase_work_acceptance.group_enforce_wa_on_invoice"
            )
            rec.require_wa = self.wa_id and enforce_wa

    @api.onchange("purchase_vendor_bill_id", "purchase_id")
    def _onchange_purchase_auto_complete(self):
        res = super()._onchange_purchase_auto_complete()
        if self.wa_id:
            self.write(
                {"ref": self.wa_id.invoice_ref, "currency_id": self.wa_id.currency_id}
            )
        return res

    def action_post(self):
        for rec in self:
            if rec.wa_id:
                wa_line = {}
                for line in rec.wa_id.wa_line_ids:
                    qty = line.product_uom._compute_quantity(
                        line.product_qty, line.product_id.uom_id
                    )
                    if qty > 0.0:
                        if line.product_id.id in wa_line.keys():
                            qty_old = wa_line[line.product_id.id]
                            wa_line[line.product_id.id] = qty_old + qty
                        else:
                            wa_line[line.product_id.id] = qty
                invoice_line = {}
                for line in rec.invoice_line_ids:
                    qty = line.product_uom_id._compute_quantity(
                        line.quantity, line.product_id.uom_id
                    )
                    if qty > 0.0:
                        if line.product_id.id in invoice_line.keys():
                            qty_old = invoice_line[line.product_id.id]
                            invoice_line[line.product_id.id] = qty_old + qty
                        else:
                            invoice_line[line.product_id.id] = qty
                if wa_line != invoice_line:
                    raise ValidationError(
                        _(
                            "You cannot validate a bill if Quantity not equal "
                            "accepted quantity"
                        )
                    )
        return super().action_post()
