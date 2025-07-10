# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from ast import literal_eval

from odoo import _, models


class ConfirmationWizard(models.TransientModel):
    _inherit = "confirmation.wizard"

    def confirm_pending_order(self, order):
        invalid_lines = order.order_line.filtered("pending_order_ids")
        if not invalid_lines:
            return
        message = invalid_lines._get_order_confirm_message()
        if not message:
            return
        return self.confirm_message(
            message,
            order,
            title=_("There are existing Requests for Quotations for:"),
            method="button_confirm",
        )

    def _create_po_activity(self, activity_type_id):
        res_ids = literal_eval(self.res_ids) if self.res_ids else []
        message = self.message

        records = self.env[self.res_model].browse(res_ids)
        model_id = self.env["ir.model"]._get_id(records._name)
        activity_type = self.env["mail.activity.type"].browse(activity_type_id)
        user_id = activity_type.default_user_id.id or self.env.user.id
        activity_type_id = activity_type.id
        activity_vals_list = []
        for record in records:
            activity_vals_list.append(
                {
                    "user_id": user_id,
                    "activity_type_id": activity_type_id,
                    "res_id": record.id,
                    "res_model_id": model_id,
                    "note": message,
                }
            )
        if activity_vals_list:
            self.env["mail.activity"].create(activity_vals_list)

    def action_confirm(self):
        action_type_id = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(
                "purchase_order_duplicate_check.repeating_orders_activity_type_id",
                False,
            )
        )
        if action_type_id:
            self._create_po_activity(int(action_type_id))
        return super().action_confirm()
