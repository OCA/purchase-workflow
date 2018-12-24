# Copyright 2018 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    purchase_request_service = fields.Boolean(
        string="Purchase Request Service",
        compute='_compute_purchase_request',
        inverse='_inverse_purchase_request',
        store=True,
        help="When this option is selected, any procurement for services"
             "raising from the inventory subsystem (like services for"
             "subcontracting in manufacturing) will translate into a purchase"
             "request."
        )

    @api.multi
    @api.depends('purchase_request')
    def _compute_purchase_request(self):
        for rec in self:
            if rec.type == 'service':
                rec.purchase_request_service = rec.purchase_request

    @api.multi
    def _inverse_purchase_request(self):
        for rec in self:
            if rec.type == 'service':
                rec.purchase_request = rec.purchase_request_service
