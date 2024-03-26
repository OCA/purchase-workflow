# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def button_confirm(self):
        """
        If partial confirmation feature is enabled,
        instead of standard PO confirmation at first we need
        to open the partial confirmation wizard for current PO.

        If feature is disabled or 'standard_confirm_proceed' context key
        was specified as True, then we proceed with standard confirmation.
        """

        force_confirm = self.env.context.get("standard_confirm_proceed", False)
        partial_confirm_enabled = self.env["ir.config_parameter"].get_param(
            "purchase_order_confirm_partial.enabled",
            False,
        )
        if force_confirm or not partial_confirm_enabled:
            return super().button_confirm()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "purchase_order_confirm_partial.purchase_order_confirm_partial_action"
        )
        action.update(
            {
                "context": {
                    "default_purchase_order_id": self.id,
                }
            }
        )
        return action

    def _process_unconfirmed_rfq(self, confirmed_lines):
        """
        If 'Save Unconfirmed Items' feature is enabled,
        then create a new RFQ in the 'Cancel' state
        and move all unconfirmed lines to it.

        Quantities of those lines should be reduced
        depending on confirmed quantities.

        If after reduction the quantity of any line
        is less than or equal to 0, then remove that line.

        Args:
            confirmed_lines: purchase.order.confirm.partial.line recordset.
            Lines to be confirmed.

        Returns:
            purchase.order: Created unconfirmed RFQ
            None: If feature is disabled or no unconfirmed lines
        """
        self.ensure_one()
        save_unconfirmed = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("purchase_order_confirm_partial.save_unconfirmed", False)
        )
        if not save_unconfirmed:
            return
        # If all lines are confirmed and confirmed quantity
        # is equal to ordered quantity, then no need to create
        # unconfirmed RFQ.
        if all(
            [
                line.confirmed_qty == line.po_line_id.product_qty
                for line in confirmed_lines
            ]
        ) and len(confirmed_lines) == len(self.order_line):
            return
        unconfirmed_suffix = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("purchase_order_confirm_partial.unconfirmed_suffix", "-U")
        )
        unconfirmed_order = self.copy(
            {
                "name": self.name + unconfirmed_suffix,
            }
        )

        # Remove order lines manually because
        # for some reason "order_line": False key in
        # copy() method parameter doesn't reset inherited lines.
        if unconfirmed_order.order_line:
            unconfirmed_order.order_line.unlink()

        for line in self.order_line:
            confirmed_line = confirmed_lines.filtered(lambda x: x.po_line_id == line)
            if confirmed_line.confirmed_qty == line.product_qty:
                continue
            line.copy(
                {
                    "order_id": unconfirmed_order.id,
                    "product_qty": line.product_qty - confirmed_line.confirmed_qty,
                }
            )
        unconfirmed_order.state = "cancel"
        unconfirmed_order.message_post(
            body=_(
                "Created from "
                "<a href=# data-oe-model=purchase.order data-oe-id=%(id)d>%(name)s</a>"
            )
            % {"id": self.id, "name": self.name},
            partner_id=self.env.ref("base.partner_root").id,
            subtype_id=self.env.ref("mail.mt_note").id,
        )
        return unconfirmed_order

    def _update_order_lines_qty(self, confirmed_lines):
        """
        Update quantities of order lines depending
        on confirmed quantities in selected lines.

        Args:
            confirmed_lines: purchase.order.confirm.partial.line recordset.
        """
        self.ensure_one()
        for line in confirmed_lines:
            line.po_line_id.product_qty = line.confirmed_qty

    def action_confirm_partial(self, confirmed_lines):
        """
        Confirms only selected lines of the PO.

        If 'Save Unconfirmed Items' feature is enabled,
        then it creates also a new RFQ in the 'Cancel' state
        containing all unconfirmed lines and quantities.

        Args:
            confirmed_lines: purchase.order.confirm.partial.line recordset.
            Lines to be confirmed.
        """
        self.ensure_one()
        unconfirmed_rfq = self._process_unconfirmed_rfq(confirmed_lines)
        self._update_order_lines_qty(confirmed_lines)
        self.with_context(
            standard_confirm_proceed=True,
            skip_alternative_check=True,
        ).button_confirm()
        if unconfirmed_rfq:
            self.message_post(
                body=_(
                    "Unconfirmed lines are saved in "
                    "<a href=# data-oe-model=purchase.order data-oe-id=%(id)d>%(name)s</a>"
                )
                % {"id": unconfirmed_rfq.id, "name": unconfirmed_rfq.name},
                partner_id=self.env.ref("base.partner_root").id,
                subtype_id=self.env.ref("mail.mt_note").id,
            )
