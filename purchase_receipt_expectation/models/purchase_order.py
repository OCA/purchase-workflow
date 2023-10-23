# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from collections import defaultdict

from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    # New values added to this selection also require the definition
    # of methods that manage such values. These methods must be named
    # `_create_picking_for_<value>_receipt_expectation()`.
    # See `_create_picking()` override.
    receipt_expectation = fields.Selection(
        [("automatic", "Automatic")],
        help="Defines how reception pickings are managed when the order is"
        " approved.\nDefault value is 'automatic', which means the"
        " picking will be created following the standard Odoo workflow.",
        default="automatic",
        required=True,
    )

    def _create_picking(self):
        if self.env.context.get("skip_custom_receipt_expectation"):
            # Shortcut; also avoids recursion errors
            return super()._create_picking()
        groups = defaultdict(list)
        for order in self:
            groups[order.receipt_expectation].append(order.id)
        for exp, order_ids in groups.items():
            orders = self.browse(order_ids)
            method = "_create_picking_for_%s_receipt_expectation" % exp
            if hasattr(orders, method):
                getattr(orders, method)()
            else:
                msg = "Method `%s.%s()` not implemented" % (self._name, method)
                raise NotImplementedError(msg)
        return True

    def _create_picking_for_automatic_receipt_expectation(self):
        """Automatic => standard picking creation workflow"""
        orders = self.with_context(skip_custom_receipt_expectation=True)
        return orders._create_picking()
