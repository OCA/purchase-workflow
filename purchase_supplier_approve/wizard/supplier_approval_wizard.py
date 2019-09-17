# Copyright 2019 RGB Consulting - Domantas Sidorenkovas
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SupplierValidationWizard(models.TransientModel):
    _name = 'supplier.approval.wizard'
    _description = 'Supplier Validation Wizard'

    supplier_approve_status = fields.Selection([
        ('pending_approve', 'Pending approval'),
        ('approved', 'Approved'),
        ('not_approved', 'Not approved'),
    ], default='pending_approve')

    def _get_partner(self):
        return self.env['res.partner'].browse(self._context.get('active_id'))

    @api.model
    def default_get(self, fields):
        result = super(SupplierValidationWizard, self).default_get(fields)
        partner_id = self._get_partner()
        if partner_id:
            result[
                'supplier_approve_status'] = partner_id.supplier_approve_status
        return result

    @api.multi
    def confirm_button(self):
        partner_id = self._get_partner()
        partner_id.supplier_approve_status = self.supplier_approve_status
