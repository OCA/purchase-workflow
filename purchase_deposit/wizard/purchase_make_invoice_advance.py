# Copyright 2019 Elico Corp, Dominique K. <dominique.k@elico-corp.com.sg>
# Copyright 2019 Ecosoft Co., Ltd., Kitti U. <kittiu@ecosoft.co.th>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import time
from datetime import datetime

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class PurchaseAdvancePaymentInv(models.TransientModel):
    _name = "purchase.advance.payment.inv"
    _description = "Purchase Advance Payment Invoice"

    advance_payment_method = fields.Selection(
        [
            ("percentage", "Down payment (percentage)"),
            ("fixed", "Deposit payment (fixed amount)"),
        ],
        string="What do you want to invoice?",
        default="percentage",
        required=True,
    )
    purchase_deposit_product_id = fields.Many2one(
        comodel_name="product.product",
        string="Deposit Payment Product",
        domain=[("type", "=", "service")],
    )
    amount = fields.Float(
        string="Deposit Payment Amount",
        required=True,
        help="The amount to be invoiced in advance, taxes excluded.",
    )
    deposit_account_id = fields.Many2one(
        comodel_name="account.account",
        string="Expense Account",
        domain=[("deprecated", "=", False)],
        help="Account used for deposits",
    )
    deposit_taxes_id = fields.Many2many(
        comodel_name="account.tax",
        string="Vendor Taxes",
        help="Taxes used for deposits",
    )

    @api.model
    def view_init(self, fields):
        active_id = self._context.get("active_id")
        purchase = self.env["purchase.order"].browse(active_id)
        if purchase.state != "purchase":
            raise UserError(_("This action is allowed only in Purchase Order sate"))
        return super().view_init(fields)

    @api.onchange("purchase_deposit_product_id")
    def _onchagne_purchase_deposit_product_id(self):
        product = self.purchase_deposit_product_id
        self.deposit_account_id = product.property_account_expense_id
        self.deposit_taxes_id = product.supplier_taxes_id

    def _prepare_deposit_val(self, order, po_line, amount):
        ir_property_obj = self.env["ir.property"]
        account_id = False
        product = self.purchase_deposit_product_id
        if product.id:
            account_id = (
                product.property_account_expense_id.id
                or product.categ_id.property_account_expense_categ_id.id
            )
        if not account_id:
            inc_acc = ir_property_obj._get(
                "property_account_expense_categ_id", "product.category"
            )
            account_id = (
                order.fiscal_position_id.map_account(inc_acc).id if inc_acc else False
            )
        if not account_id:
            raise UserError(
                _(
                    "There is no purchase account defined for this product: %s."
                    "\nYou may have to install a chart of account from "
                    "Accounting app, settings menu."
                )
                % (product.name,)
            )

        if self.amount <= 0:
            raise UserError(_("The value of the deposit must be positive."))
        context = {"lang": order.partner_id.lang}
        amount = self.amount
        if self.advance_payment_method == "percentage":  # Case percent
            if self.amount > 100:
                raise UserError(_("The percentage of the deposit must be not over 100"))
            amount = self.amount / 100 * order.amount_untaxed
        name = _("Deposit Payment")
        del context
        taxes = product.supplier_taxes_id.filtered(
            lambda r: not order.company_id or r.company_id == order.company_id
        )
        if order.fiscal_position_id and taxes:
            tax_ids = order.fiscal_position_id.map_tax(taxes).ids
        else:
            tax_ids = taxes.ids

        deposit_val = {
            "invoice_origin": order.name,
            "move_type": "in_invoice",
            "partner_id": order.partner_id.id,
            "invoice_line_ids": [
                (
                    0,
                    0,
                    {
                        "name": name,
                        "account_id": account_id,
                        "price_unit": amount,
                        "quantity": 1.0,
                        "product_uom_id": product.uom_id.id,
                        "product_id": product.id,
                        "purchase_line_id": po_line.id,
                        "tax_ids": [(6, 0, tax_ids)],
                        "analytic_account_id": po_line.account_analytic_id.id or False,
                    },
                )
            ],
            "currency_id": order.currency_id.id,
            "invoice_payment_term_id": order.payment_term_id.id,
            "fiscal_position_id": order.fiscal_position_id.id
            or order.partner_id.property_account_position_id.id,
            "purchase_id": order.id,
            "narration": order.notes,
        }
        return deposit_val

    def _create_invoice(self, order, po_line, amount):
        Invoice = self.env["account.move"]
        deposit_val = self._prepare_deposit_val(order, po_line, amount)
        invoice = Invoice.create(deposit_val)
        invoice.message_post_with_view(
            "mail.message_origin_link",
            values={"self": invoice, "origin": order},
            subtype_id=self.env.ref("mail.mt_note").id,
        )
        return invoice

    def create_invoices(self):
        Purchase = self.env["purchase.order"]
        IrDefault = self.env["ir.default"].sudo()
        purchases = Purchase.browse(self._context.get("active_ids", []))
        # Create deposit product if necessary
        product = self.purchase_deposit_product_id
        if not product:
            vals = self._prepare_deposit_product()
            product = self.purchase_deposit_product_id = self.env[
                "product.product"
            ].create(vals)
            IrDefault.set(
                "purchase.advance.payment.inv",
                "purchase_deposit_product_id",
                product.id,
            )
        PurchaseLine = self.env["purchase.order.line"]
        for order in purchases:
            amount = self.amount
            if self.advance_payment_method == "percentage":  # Case percent
                amount = self.amount / 100 * order.amount_untaxed
            if product.purchase_method != "purchase":
                raise UserError(
                    _(
                        "The product used to invoice a down payment should have "
                        'an invoice policy set to "Ordered quantities". '
                        "Please update your deposit product to be able to "
                        "create a deposit invoice."
                    )
                )
            if product.type != "service":
                raise UserError(
                    _(
                        "The product used to invoice a down payment should be "
                        'of type "Service". Please use another product or '
                        "update this product."
                    )
                )
            taxes = product.supplier_taxes_id.filtered(
                lambda r: not order.company_id or r.company_id == order.company_id
            )
            if order.fiscal_position_id and taxes:
                tax_ids = order.fiscal_position_id.map_tax(taxes).ids
            else:
                tax_ids = taxes.ids
            context = {"lang": order.partner_id.lang}
            po_line = PurchaseLine.create(
                {
                    "name": _("Advance: %s") % (time.strftime("%m %Y"),),
                    "price_unit": amount,
                    "product_qty": 0.0,
                    "order_id": order.id,
                    "product_uom": product.uom_id.id,
                    "product_id": product.id,
                    "taxes_id": [(6, 0, tax_ids)],
                    "date_planned": datetime.today().strftime(
                        DEFAULT_SERVER_DATETIME_FORMAT
                    ),
                    "is_deposit": True,
                }
            )
            del context

            if self._context.get("create_bills", False):
                self._create_invoice(order, po_line, amount)
                return purchases.action_view_invoice()
        return {"type": "ir.actions.act_window_close"}

    def _prepare_deposit_product(self):
        return {
            "name": "Purchase Deposit",
            "type": "service",
            "purchase_method": "purchase",
            "property_account_expense_id": self.deposit_account_id.id,
            "supplier_taxes_id": [(6, 0, self.deposit_taxes_id.ids)],
            "company_id": False,
        }
