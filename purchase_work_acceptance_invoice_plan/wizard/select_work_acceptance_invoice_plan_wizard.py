# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SelectWorkAcceptanceInvoicePlanWizard(models.TransientModel):
    _name = "select.work.acceptance.invoice.plan.wizard"
    _description = "Select Work Acceptance Invoice Plan Wizard"

    active_installment_ids = fields.Many2many(
        comodel_name="purchase.invoice.plan",
        compute="_compute_active_installment_ids",
    )
    installment_id = fields.Many2one(
        comodel_name="purchase.invoice.plan",
        string="Invoice Plan",
        required=True,
        domain="[('id', 'in', active_installment_ids)]",
        help="List only installment that has not been used in WA (draft, accepted)",
    )

    @api.depends("installment_id")
    def _compute_active_installment_ids(self):
        self.ensure_one()
        purchase = self.env["purchase.order"].browse(
            self._context.get("active_ids", [])
        )
        installment_ids = (
            purchase.wa_ids.filtered(lambda l: l.state != "cancel")
            .mapped("installment_id")
            .ids
        )
        self.active_installment_ids = self.env["purchase.invoice.plan"].search(
            [("purchase_id", "=", purchase.id), ("id", "not in", installment_ids)]
        )

    def button_create_wa(self):
        purchase = self.env["purchase.order"].browse(self._context.get("active_id"))
        if self.installment_id not in self.active_installment_ids:
            raise UserError(
                _(
                    "Installment {} is already used by other WA.".format(
                        self.installment_id.installment
                    )
                )
            )
        res = purchase.with_context(
            installment_id=self.installment_id.id
        ).action_view_wa()
        res["context"]["default_installment_id"] = self.installment_id.id
        return res
