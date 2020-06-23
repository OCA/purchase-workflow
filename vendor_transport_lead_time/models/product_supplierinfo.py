# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductSupplierinfo(models.Model):

    _inherit = "product.supplierinfo"

    delay = fields.Integer(
        string="Lead Time",
        compute="_compute_delay",
        inverse="_inverse_delay",
        readonly=True,
    )
    supplier_delay = fields.Integer(
        string="Supplier Lead Time", default=0, required=True
    )
    transport_delay = fields.Integer(
        string="Transport Lead Time", default=0, required=True
    )

    @api.depends("supplier_delay", "transport_delay")
    def _compute_delay(self):
        for record in self:
            record.delay = record.supplier_delay + record.transport_delay

    def _inverse_delay(self):
        for record in self:
            diff = record.delay - record.transport_delay
            if diff < 0:
                raise ValidationError(
                    _("You can't set a delay inferior to the transport delay.")
                )
            else:
                record.supplier_delay = diff
