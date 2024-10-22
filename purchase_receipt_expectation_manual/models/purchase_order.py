# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    receipt_expectation = fields.Selection(
        selection_add=[("manual", "Manual")],
        ondelete={"manual": "set default"},
    )

    def _create_picking_for_manual_receipt_expectation(self):
        """Manual => do nothing, users will create picking via the wizard"""
        return self

    def button_open_manual_receipt_wizard(self):
        self.ensure_one()
        wiz = self._prepare_manual_receipt_wizard()
        return wiz.open_form_view()

    def _prepare_manual_receipt_wizard(self):
        """Creates a manual receipt wizard

        Used to pre-fill wizard data before opening the form view
        """
        self.ensure_one()
        vals = self._prepare_manual_receipt_wizard_vals()
        return self.env["purchase.order.manual.receipt.wizard"].create(vals)

    def _prepare_manual_receipt_wizard_vals(self) -> dict:
        self.ensure_one()
        line_vals = self._prepare_manual_receipt_wizard_line_vals_list()
        return {
            "purchase_order_id": self.id,
            "line_ids": [(0, 0, v) for v in line_vals],
        }

    def _prepare_manual_receipt_wizard_line_vals_list(self) -> list:
        self.ensure_one()
        return self.order_line._prepare_manual_receipt_wizard_line_vals_list()
