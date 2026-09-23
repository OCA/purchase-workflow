from odoo import api, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def message_subscribe(self, partner_ids=None, subtype_ids=None):
        partner_ids = partner_ids or []
        if (
            self._context.get("purchase_partner_disable_autofollow")
            and self.partner_id.id in partner_ids
        ):
            partner_ids.remove(self.partner_id.id)
        return super().message_subscribe(partner_ids, subtype_ids)

    @api.model_create_multi
    def create(self, values):
        autofollow_disabled = self._partner_disable_autofollow()
        orders = super(
            PurchaseOrder,
            self.with_context(purchase_partner_disable_autofollow=autofollow_disabled),
        ).create(values)

        if not autofollow_disabled:
            for order in orders:
                if (
                    order.partner_id
                    and order.partner_id.id not in order.message_partner_ids.ids
                ):
                    order.message_subscribe([order.partner_id.id])

        return orders

    def button_confirm(self):
        self = self.with_context(
            purchase_partner_disable_autofollow=self._partner_disable_autofollow()
        )
        return super().button_confirm()

    def _partner_disable_autofollow(self):
        """Returns the state of the "Customer disable autofollow" option

        Returns:
            bool: Option status
        """
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(
                "purchase_order_partner_no_autofollow.partner_disable_autofollow", False
            )
        )
