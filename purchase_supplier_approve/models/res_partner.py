# Copyright 2019 RGB Consulting - Domantas Sidorenkovas
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    supplier_approve_status = fields.Selection([
        ('pending_approve', 'Pending approval'),
        ('approved', 'Approved'),
        ('not_approved', 'Not approved'),
    ], default='pending_approve', readonly=True, track_visibility='onchange',
        help=" * The 'Pending approval' is the default state. In this state "
             "the supplier is still pending approval.\n"
             " * The 'Approved' state indicates that this supplier is "
             "approved and his purchase quotations can be confirmed.\n"
             " * The 'Not approved' state is used to specify that the "
             "supplier information was rejected.\n")

    @api.model
    def create(self, vals):
        res = super(ResPartner, self).create(vals)
        if res.parent_id:
            res.supplier_approve_status = res.parent_id.supplier_approve_status
        return res
