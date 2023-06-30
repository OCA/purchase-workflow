# Copyright 2023 Forgeflow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    related_po_sequence = fields.Char(
        string="PO Line Number",
        compute="_compute_related_po_sequence",
    )

    @api.depends("move_id.invoice_line_ids")
    def _compute_related_po_sequence(self):
        for rec in self:
            if len(rec.move_id.mapped("line_ids.purchase_order_id")) > 1:
                rec.related_po_sequence = "{}/{}".format(
                    rec.purchase_line_id.order_id.name,
                    rec.purchase_line_id.visible_sequence,
                )
            else:
                rec.related_po_sequence = str(rec.purchase_line_id.visible_sequence)
