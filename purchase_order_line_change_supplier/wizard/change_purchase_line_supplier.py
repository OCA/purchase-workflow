# -*- coding: utf-8 -*-
# Copyright 2019 PlanetaTIC - Marc Poch <mpoch@planetatic.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError


class ChangePurchaseLineSupplierWizard(models.TransientModel):
    """
        A wizard to change purchase order line's supplier.
    """

    _name = 'change.purchase.line.supplier.wizard'
    _description = 'Change Purchase Line Supplier Wizard'

    supplier_id = fields.Many2one(
        'res.partner', string='Supplier', domain=[('supplier', '=', True)],
        required=True)

    @api.multi
    def confirm_change_purchase_lines_supplier(self):
        purchase_line_obj = self.env['purchase.order.line']

        self.ensure_one()

        purchase_line_ids = self._context.get('active_ids', False)
        if not purchase_line_ids:
            raise UserError(_('There are no lines to change supplier.'))
        purchase_lines = purchase_line_obj.browse(purchase_line_ids)

        purchase_id = purchase_lines.change_supplier(self.supplier_id.id)

        return {
            'name': _('Request for Quotation'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'purchase.order',
            'view_id': self.env.ref('purchase.purchase_order_form').id,
            'type': 'ir.actions.act_window',
            'res_id': purchase_id,
            'context': self.env.context,
            'target': 'current',
        }
