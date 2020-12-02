# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductSupplierinfo(models.Model):

    _inherit = "product.supplierinfo"

    delay = fields.Integer(
        compute="_compute_delay", inverse="_inverse_delay", store=True, required=False
    )
    supplier_delay = fields.Integer(
        string="Supplier Lead Time",
        default=0,
        required=True,
        help="Supplier lead time in days.",
    )
    transport_delay = fields.Integer(
        string="Transport Lead Time",
        default=0,
        required=True,
        help="Transport lead time in days.",
    )

    @api.depends("supplier_delay", "transport_delay")
    def _compute_delay(self):
        for record in self:
            record.delay = record.supplier_delay + record.transport_delay

    def _inverse_delay(self):
        for record in self:
            record.supplier_delay = record.delay - record.transport_delay

    @api.constrains("supplier_delay")
    def _check_delay(self):
        for seller in self:
            if seller.supplier_delay < 0:
                raise ValidationError(
                    _("You can't set a delay inferior to the transport delay.")
                )

    @api.model
    def _setup_fields(self):
        # "remove" the default lambda on "delay" field (from 'product' module)
        # to not let Odoo put a value in this field when 'create' is called
        self._fields["delay"].default = False
        super()._setup_fields()
