# Copyright 2023 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import models


class MailComposeMessage(models.TransientModel):
    _inherit = "mail.compose.message"

    def action_send_mail(self, **kwargs):
        res = super().action_send_mail(**kwargs)
        context = self.env.context
        if context.get("active_model") == "purchase.order" and context.get(
            "mark_rfq_as_sent"
        ):
            rfq = self.env["purchase.order"].browse(context["active_ids"])
            rfq.filtered(lambda o: o.state == "draft").write({"state": "sent"})
        return res
