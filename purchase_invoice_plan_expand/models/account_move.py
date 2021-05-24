# Copyright 2021 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "invoice_line_ids" in vals:
                invoice_line_ids = list(
                    filter(
                        lambda l: isinstance(l, tuple)
                        and len(l) == 3
                        and not l[2].get("force_remove_this"),
                        vals["invoice_line_ids"],
                    )
                )
                vals["invoice_line_ids"] = list(invoice_line_ids)
        return super().create(vals_list)
