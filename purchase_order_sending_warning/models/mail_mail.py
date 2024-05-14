# Copyright 2024 Camptocamp
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class MailMail(models.Model):
    _inherit = "mail.mail"

    def write(self, vals):
        res = super().write(vals)
        po_mails = self.filtered_domain([("model", "=", "purchase.order")])
        if po_mails:
            error = vals.get("state") == "exception"
            records = self.env["purchase.order"].browse(po_mails.mapped("res_id"))
            records.write({"sending_error_type": "email_not_sent" if error else False})
        return res
