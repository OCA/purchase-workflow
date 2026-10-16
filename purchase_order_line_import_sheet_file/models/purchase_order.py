# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, models
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _check_order_line_import_state(self):
        if self.filtered(lambda order: order.state not in ("draft", "sent")):
            raise UserError(
                _("Lines can only be imported into a request for quotation.")
            )

    def action_open_line_import(self):
        self.ensure_one()
        self._check_order_line_import_state()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "purchase_order_line_import_sheet_file.purchase_order_line_import_action"
        )
        action["context"] = {"default_order_id": self.id}
        return action
