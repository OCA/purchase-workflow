# Copyright (C) 2021-Today GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    state = fields.Selection(selection_add=[("draft", "Draft"), ("sent", "Sent")])

    def print_quotation(self):
        # Allows printing orders in 'draft' state by changing them to 'sent'
        # before generating the report.
        orders = self.filtered(lambda x: x.state == "draft")
        orders.write({"state": "sent"})
        report = self.env.ref("purchase.action_report_purchase_order")
        return report.report_action(self)
