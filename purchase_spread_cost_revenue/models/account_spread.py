# Copyright 2024 Ecosoft (<https://ecosoft.co.th>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountSpread(models.Model):
    _inherit = "account.spread"

    purchase_line_id = fields.Many2one(
        "purchase.order.line",
        string="Purchase order line",
    )
    purchase_id = fields.Many2one(
        related="purchase_line_id.order_id",
        readonly=True,
        store=True,
    )

    @api.model
    def create(self, vals):
        res = super().create(vals)
        if vals.get("purchase_line_id"):
            pline = self.env["purchase.order.line"].browse(vals["purchase_line_id"])
            pline.write({"spread_id": res.id})
        return res

    @api.depends(
        "estimated_amount",
        "currency_id",
        "company_id",
        "invoice_line_id.price_subtotal",
        "invoice_line_id.currency_id",
        "purchase_line_id.price_subtotal",
        "purchase_line_id.currency_id",
        "line_ids.amount",
        "line_ids.move_id.state",
    )
    def _compute_amounts(self):
        for spread in self:
            if spread.purchase_line_id:
                spread.estimated_amount = spread.purchase_line_id.price_subtotal
        res = super()._compute_amounts()
        return res

    def action_unlink_purchase_line(self):
        """Unlink the purchase line from the spread board"""
        self.ensure_one()
        if self.purchase_id.state != "draft":
            msg = _("Cannot unlink purchase lines if the purchase order is validated")
            raise UserError(msg)
        self._action_unlink_purchase_line()

    def _action_unlink_purchase_line(self):
        self._message_post_unlink_purchase_line()
        self.purchase_line_id.spread_id = False
        self.purchase_line_id = False

    def _message_post_unlink_purchase_line(self):
        for spread in self:
            po_link = "<a href=# data-oe-model=account.move " "data-oe-id=%d>%s</a>" % (
                spread.purchase_id.id,
                _("Purchase Order"),
            )
            msg_body = _(
                "Unlinked invoice line '%(spread_line_name)s' (view %(po_link)s)."
            ) % {
                "spread_line_name": spread.purchase_line_id.name,
                "po_link": po_link,
            }
            spread.message_post(body=msg_body)
            spread_link = (
                "<a href=# data-oe-model=account.spread "
                "data-oe-id=%d>%s</a>" % (spread.id, _("Spread"))
            )
            msg_body = _("Unlinked '%(spread_link)s' (purchase line %(po_line)s).") % {
                "spread_link": spread_link,
                "po_line": spread.purchase_line_id.name,
            }
            spread.purchase_id.message_post(body=msg_body)

    def _compute_spread_board(self):
        self.ensure_one()
        if self.invoice_line_id.spread_on_purchase:
            return
        super()._compute_spread_board()
