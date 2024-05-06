# Copyright 2024 Camptocamp
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class MailMail(models.Model):
    _inherit = "mail.mail"

    def write(self, vals):
        res = super(MailMail, self).write(vals)
        if vals.get("state") == "exception":
            for mail in self:
                if mail.model == "purchase.order":
                    order = self.env["purchase.order"].browse(mail.res_id)
                    order.sending_warning = "email_not_sent"
        else:
            for mail in self:
                if mail.model == "purchase.order":
                    order = self.env["purchase.order"].browse(mail.res_id)
                    order.sending_warning = False
        return res
