# Copyright 2013 Guewen Baconnier, Camptocamp SA
# Copyright 2017 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    cancel_reason_id = fields.Many2one(
        comodel_name="purchase.order.cancel.reason",
        string="Reason for cancellation",
        readonly=True,
        ondelete="restrict",
    )
