# Copyright 2023 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)


from odoo import _, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def action_all_rfq_related_send(self):
        template = self.env.ref("purchase.email_template_edi_purchase", False)
        compose_form = self.env.ref(
            "mail.email_compose_message_wizard_form",
            False,
        )
        ctx = dict(
            self.env.context,
            default_model="purchase.order",
            active_model="purchase.order",
            active_id=self.ids[0],
            active_ids=self.ids,
            default_template_id=template and template.id,
            default_composition_mode="mass_mail",
            mark_rfq_as_sent=True,
        )

        return {
            "name": _("Mass mailing for purchases"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "mail.compose.message",
            "views": [(compose_form.id, "form")],
            "view_id": compose_form.id,
            "target": "new",
            "context": ctx,
        }
