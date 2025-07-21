# Copyright (C) 2021-Today GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    # Renaming the user-facing labels for the existing states `draft` and `sent`
    # without adding new states. These are already defined in the purchase module.
    state = fields.Selection(
        selection_add=[
            ("draft", "Draft"),
            ("sent", "Sent"),
        ]
    )

    def print_quotation(self):
        # This method is intentionally overloaded to redefine its functionality.
        # Note: We are breaking the inheritance chain here by not calling super(),
        orders = self.filtered(lambda x: x.state == "draft")
        orders.write({"state": "sent"})
        report = self.env.ref("purchase.action_report_purchase_order")
        return report.report_action(self)
