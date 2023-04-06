# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "res.partner"

    @api.model
    def _get_receipt_expectation_selection(self):
        po_field = self.env["purchase.order"]._fields["receipt_expectation"]
        return po_field.selection

    receipt_expectation = fields.Selection(_get_receipt_expectation_selection)
