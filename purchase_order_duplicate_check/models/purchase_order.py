from odoo import models, tools


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _prepare_pending_orders_message(self, product_id):
        """
        Prepare pending order line message

        :param product_id: product.product record id
        :return str: message
        """
        message_parts = []
        order_lines = self.order_line.filtered(lambda l: l.product_id.id == product_id)
        for line in order_lines:
            order = line.order_id
            order_href = (
                f"<a href='/web#id={order.id}&model={order._name}'>{order.name}</a>"
            )
            type_ = order.state in ["draft", "sent"] and "RFQ" or "PO"
            message_parts.append(
                f"{type_}: {order_href}; date: {order.create_date.date()}; Qty: {line.product_qty};<br/>"  # noqa
            )
        return "".join(message_parts)

    def _check_pending_order(self):
        """Check for pending orders and trigger confirmation wizard if needed."""
        if not tools.config["test_enable"] or self._context.get(
            "test_purchase_duplicate_check"
        ):
            action = self.env["confirmation.wizard"].confirm_pending_order(self)
            if action:
                return action

    def button_confirm(self):
        """
        Confirm the purchase order.

        :return: action or super
        """
        action = self._check_pending_order()
        return action or super().button_confirm()
