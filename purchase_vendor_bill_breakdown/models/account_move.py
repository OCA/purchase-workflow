from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model_create_multi
    def create(self, vals_list):
        # Handle component invoice line values
        for key, vals in enumerate(vals_list, start=0):
            vals_list[key]["invoice_line_ids"] = [
                (i, j, line)
                for i, j, line in vals.get("invoice_line_ids", [])
                if not line.get("skip_record")
            ]
        return super(AccountMove, self).create(vals_list)


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    component_qty = fields.Float(default=0.0)
