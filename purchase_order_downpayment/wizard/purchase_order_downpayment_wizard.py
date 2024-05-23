from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PurchaseOrderDownPaymentWizard(models.TransientModel):
    _name = "purchase.order.down.payment.wizard"
    _description = "Purchase Order DownPayment Wizard"

    order_id = fields.Many2one("purchase.order", required=True)

    advance_payment_method = fields.Selection(
        selection=[
            ("delivered", "Regular Payment"),
            ("percentage", "Down payment (percentage)"),
            ("fixed", "Down payment (fixed amount)"),
        ],
        string="Create Payment",
        default="delivered",
        required=True,
    )

    amount = fields.Float(string="Down Payment Amount")
    fixed_amount = fields.Float(
        string="Down Payment Amount (Fixed)",
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        purchase_id = self.env.context.get("active_id")
        if not purchase_id:
            return res
        purchase_id = self.env["purchase.order"].browse(purchase_id)
        if purchase_id:
            res.update(
                {
                    "order_id": purchase_id.id,
                }
            )

        return res

    @api.constrains("advance_payment_method", "amount", "fixed_amount")
    def _check_amount_is_positive(self):
        for wizard in self:
            if wizard.advance_payment_method == "percentage" and (
                wizard.amount <= 0 or wizard.amount > 100
            ):
                raise UserError(
                    _(
                        "The value of the down payment percentage cannot be greater than 100%."
                    )
                )
            elif (
                wizard.advance_payment_method == "fixed" and wizard.fixed_amount <= 0.00
            ):
                raise UserError(
                    _("The value of the down payment amount must be positive.")
                )

    def _get_down_payment_amount(self, order):
        self.ensure_one()
        if self.advance_payment_method == "delivered":
            amount = order.amount_total
        elif self.advance_payment_method == "percentage":
            amount = order.amount_total * self.amount / 100
        else:
            amount = self.fixed_amount
        return amount

    def create_payment(self):
        self.ensure_one()
        payment_obj = self.env["account.payment"]
        if self.order_id:
            amount_advance = self._get_down_payment_amount(self.order_id)
            payment = payment_obj.create(
                {
                    "date": fields.date.today(),
                    "amount": amount_advance,
                    "payment_type": "outbound",
                    "partner_type": "supplier",
                    "ref": self.order_id.name,
                    "currency_id": self.order_id.currency_id.id,
                    "partner_id": self.order_id.partner_id.id,
                    "payment_method_id": self.env.ref(
                        "account.account_payment_method_manual_in"
                    ).id,
                    "purchase_id": self.order_id.id,
                }
            )

            if self.env.context.get("view_payment"):
                action = self.env["ir.actions.actions"]._for_xml_id(
                    "account.action_account_payments_payable"
                )
                action.update({"domain": [("id", "=", payment.id)]})
                return action

        return {
            "type": "ir.actions.act_window_close",
        }
