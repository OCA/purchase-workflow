from odoo import fields, models
from odoo.fields import first


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    account_payment_line_ids = fields.One2many(
        "account.payment.line",
        "purchase_id",
        string="Purchase Payment line",
    )

    def _get_communication(self):
        """Retrieve the communication string for the payment order."""
        communication_type = "normal"
        if self.partner_ref:
            communication = self.partner_ref or "" + "_" + self.name or ""
        else:
            communication = self.name or ""
        return communication_type, communication

    def _prepare_payment_line_vals(self, payment_order, amount_advance):
        self.ensure_one()
        communication_type, communication = self._get_communication()
        if self.currency_id:
            currency_id = self.currency_id.id
        else:
            currency_id = self.company_id.currency_id.id
        partner_bank_id = first(self.partner_id.bank_ids).id
        vals = {
            "order_id": payment_order.id,
            "partner_bank_id": partner_bank_id,
            "partner_id": self.partner_id.id,
            "purchase_id": self.id,
            "communication": communication,
            "communication_type": communication_type,
            "currency_id": currency_id,
            "amount_currency": amount_advance,
            "date": False,
            # date is set when the user confirms the payment order
        }
        return vals

    def create_payment_line_from_purchase(self, payment_order, amount_advance):
        vals_list = []
        for po in self:
            vals_list.append(
                po._prepare_payment_line_vals(payment_order, amount_advance)
            )
        return self.env["account.payment.line"].create(vals_list)
