from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PurchaseOrderDownPaymentWizard(models.TransientModel):
    _inherit = "purchase.order.down.payment.wizard"

    payment_mode_id = fields.Many2one(
        "account.payment.mode",
        check_company=True,
    )
    company_id = fields.Many2one(
        "res.company",
        related="order_id.company_id",
        store=True,
    )

    @api.depends("bank_partner_id")
    def _compute_partner_bank_id(self):
        for move in self:
            # This will get the bank account from the partner in an order with the trusted first
            bank_ids = move.bank_partner_id.bank_ids.filtered(
                lambda bank: not bank.company_id or bank.company_id == move.company_id
            ).sorted(lambda bank: not bank.allow_out_payment)
            move.partner_bank_id = bank_ids[:1]

    def get_account_payment_domain(self, payment_mode):
        return [("payment_mode_id", "=", payment_mode.id), ("state", "=", "draft")]

    def _prepare_new_payment_order(self, payment_mode=None):
        self.ensure_one()
        if payment_mode is None:
            payment_mode = self.env["account.payment.mode"]
        vals = {"payment_mode_id": payment_mode.id or self.payment_mode_id.id}
        # other important fields are set by the inherit of create
        # in account_payment_order.py
        return vals

    def create_payment(self):
        self.ensure_one()
        if self.payment_mode_id and self.payment_mode_id.payment_order_ok:
            action_payment_type = "debit"
            apoo = self.env["account.payment.order"]
            payorder = apoo.search(
                self.get_account_payment_domain(self.payment_mode_id), limit=1
            )
            new_payorder = False
            if payorder:
                payment_line_for_purchase = payorder.payment_line_ids.filtered(
                    lambda x: x.purchase_id == self.order_id
                )
                if payment_line_for_purchase:
                    raise UserError(
                        _(
                            "The payment line already exists in the payment order %(name)s",
                            name=payorder.name,
                        )
                    )

            else:
                payorder = apoo.create(
                    self._prepare_new_payment_order(self.payment_mode_id)
                )
                new_payorder = True
            action_payment_type = payorder.payment_type
            amount_advance = self._get_down_payment_amount(self.order_id)
            self.order_id.create_payment_line_from_purchase(payorder, amount_advance)
            if new_payorder:
                self.order_id.message_post(
                    body=_(
                        "payment line added to the new draft payment "
                        "order <a href=# data-oe-model=account.payment.order "
                        "data-oe-id=%(order_id)d>%(name)s</a>, which has been "
                        "automatically created.",
                        order_id=payorder.id,
                        name=payorder.name,
                    )
                )
            else:
                self.order_id.message_post(
                    body=_(
                        "payment line added to the existing draft "
                        "payment order "
                        "<a href=# data-oe-model=account.payment.order "
                        "data-oe-id=%(order_id)d>%(name)s</a>.",
                        order_id=payorder.id,
                        name=payorder.name,
                    )
                )
            action = self.env["ir.actions.act_window"]._for_xml_id(
                "account_payment_order.account_payment_order_%s_action"
                % action_payment_type,
            )
            action.update(
                {
                    "view_mode": "form,tree,pivot,graph",
                    "res_id": payorder.id,
                    "views": False,
                }
            )
            return action
        else:
            return super().create_payment()
