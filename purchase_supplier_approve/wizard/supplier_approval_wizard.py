# Copyright 2019 RGB Consulting - Domantas Sidorenkovas
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SupplierValidationWizard(models.TransientModel):
    _name = "supplier.approval.wizard"
    _description = "Supplier Validation Wizard"

    def _default_partner(self):
        return self.env['res.partner'].browse(self._context.get('active_id'))

    partner_id = fields.Many2one(comodel_name='res.partner',
                                 default=_default_partner, string='Supplier')

    supplier_approval = fields.Selection([
        ('pda', 'Pending approval'),
        ('apd', 'Approved'),
        ('nad', 'Not approved'),
    ], default='pda', track_visibility='onchange')

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            self.supplier_approval = self.partner_id.supplier_approval

    @api.multi
    def confirm_button(self):
        self.partner_id.supplier_approval = self.supplier_approval
