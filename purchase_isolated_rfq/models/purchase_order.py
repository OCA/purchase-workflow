# Copyright 2020 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    order_sequence = fields.Boolean(string="Order Sequence", readonly=True, index=True)
    quote_id = fields.Many2one(
        comodel_name="purchase.order",
        string="Quotation",
        readonly=True,
        ondelete="restrict",
        copy=False,
        help="For Purchases Order, this field references to its RFQ",
    )
    purchase_order_id = fields.Many2one(
        comodel_name="purchase.order",
        string="Order",
        readonly=True,
        ondelete="restrict",
        copy=False,
        help="For RFQ, this field references to its Purchases Order",
    )
    rfq_state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("sent", "Mail Sent"),
            ("cancel", "Cancelled"),
            ("done", "Done"),
        ],
        string="RFQ Status",
        readonly=True,
        related="state",
        help="Only relative RFQ states",
    )

    @api.model
    def create(self, vals):
        order_sequence = vals.get("order_sequence") or self.env.context.get(
            "order_sequence"
        )
        if not order_sequence and vals.get("name", "/") == "/":
            vals["name"] = self.env["ir.sequence"].next_by_code("purchase.rfq") or "/"
        return super().create(vals)

    def _prepare_order_from_rfq(self):
        return {
            "name": self.env["ir.sequence"].next_by_code("purchase.order") or "/",
            "order_sequence": True,
            "quote_id": self.id,
            "partner_ref": self.partner_ref,
        }

    def action_convert_to_order(self):
        self.ensure_one()
        if self.order_sequence:
            raise UserError(_("Only quotation can convert to order"))
        purchase_order = self.copy(self._prepare_order_from_rfq())
        purchase_order.button_confirm()
        # Reference from this RFQ to Purchase Order
        self.purchase_order_id = purchase_order.id
        if self.state == "draft":
            self.button_done()
        return self.open_duplicated_purchase_order()

    @api.model
    def open_duplicated_purchase_order(self):
        return {
            "name": _("Purchases Order"),
            "view_mode": "form",
            "view_id": False,
            "res_model": "purchase.order",
            "context": {"default_order_sequence": True, "order_sequence": True},
            "type": "ir.actions.act_window",
            "nodestroy": True,
            "target": "current",
            "domain": "[('order_sequence', '=', True)]",
            "res_id": self.purchase_order_id and self.purchase_order_id.id or False,
        }
